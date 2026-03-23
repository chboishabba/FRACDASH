from __future__ import annotations

import ctypes
import os
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from gpu.dashicore_bridge import import_dashicore_module
from gpu.fractran_layout import CompiledFractranLayout


SHADER_PATH = Path(__file__).resolve().parents[1] / "gpu_shaders" / "fractran_step.comp"
SPV_PATH = Path(__file__).resolve().parents[1] / "spv" / "fractran_step.spv"
DEFAULT_ICD_CANDIDATES = (
    Path("/usr/share/vulkan/icd.d/radeon_icd.x86_64.json"),
    Path("/usr/share/vulkan/icd.d/amd_icd64.json"),
    Path("/usr/share/vulkan/icd.d/nvidia_icd.json"),
)


@dataclass(frozen=True)
class FractranStepResult:
    next_exponents: np.ndarray
    selected_rule: int
    halted: bool


@dataclass(frozen=True)
class FractranBatchStepResult:
    next_exponents: np.ndarray
    selected_rules: np.ndarray
    halted: np.ndarray


@dataclass(frozen=True)
class FractranBatchProfiledResult:
    next_exponents: np.ndarray
    selected_rules: np.ndarray
    halted: np.ndarray
    phase_seconds: dict[str, float]


def ensure_default_icd() -> str | None:
    existing = os.environ.get("VK_ICD_FILENAMES")
    if existing:
        return existing
    for candidate in DEFAULT_ICD_CANDIDATES:
        if candidate.is_file():
            os.environ["VK_ICD_FILENAMES"] = str(candidate)
            return str(candidate)
    return None


class VulkanFractranStepper:
    def __init__(self) -> None:
        ensure_default_icd()
        self.gpu_common_methods = import_dashicore_module("gpu_common_methods")
        self.gpu_vulkan_dispatcher = import_dashicore_module("gpu_vulkan_dispatcher")
        self.vk = import_dashicore_module("gpu_vulkan_dispatcher").vk
        self.gpu_vulkan_dispatcher._require_vk()
        self.gpu_common_methods.compile_shader(SHADER_PATH, SPV_PATH)
        self.handles = self.gpu_vulkan_dispatcher.create_vulkan_handles(
            self.gpu_vulkan_dispatcher.VulkanDispatchConfig(device_index=0)
        )
        self.device = self.handles.device
        self.queue = self.handles.queue
        self.mem_props = self.handles.mem_props
        self.queue_family_index = self.handles.queue_family_index
        self._build_pipeline()

    def _build_pipeline(self) -> None:
        vk = self.vk
        bindings = [
            vk.VkDescriptorSetLayoutBinding(
                binding=ix,
                descriptorType=vk.VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,
                descriptorCount=1,
                stageFlags=vk.VK_SHADER_STAGE_COMPUTE_BIT,
                pImmutableSamplers=None,
            )
            for ix in range(6)
        ]
        layout_info = vk.VkDescriptorSetLayoutCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO,
            bindingCount=len(bindings),
            pBindings=bindings,
        )
        self.descriptor_set_layout = vk.vkCreateDescriptorSetLayout(self.device, layout_info, None)

        push_constant_range = vk.VkPushConstantRange(
            stageFlags=vk.VK_SHADER_STAGE_COMPUTE_BIT,
            offset=0,
            size=12,
        )
        pipeline_layout_info = vk.VkPipelineLayoutCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
            setLayoutCount=1,
            pSetLayouts=[self.descriptor_set_layout],
            pushConstantRangeCount=1,
            pPushConstantRanges=[push_constant_range],
        )
        self.pipeline_layout = vk.vkCreatePipelineLayout(self.device, pipeline_layout_info, None)

        shader_code = SPV_PATH.read_bytes()
        module_info = vk.VkShaderModuleCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
            codeSize=len(shader_code),
            pCode=shader_code,
        )
        self.shader_module = vk.vkCreateShaderModule(self.device, module_info, None)

        stage_info = vk.VkPipelineShaderStageCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
            stage=vk.VK_SHADER_STAGE_COMPUTE_BIT,
            module=self.shader_module,
            pName="main",
        )
        pipeline_info = vk.VkComputePipelineCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO,
            stage=stage_info,
            layout=self.pipeline_layout,
        )
        self.pipeline = vk.vkCreateComputePipelines(self.device, vk.VK_NULL_HANDLE, 1, [pipeline_info], None)[0]

        pool_sizes = [vk.VkDescriptorPoolSize(type=vk.VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, descriptorCount=12)]
        pool_info = vk.VkDescriptorPoolCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO,
            maxSets=2,
            poolSizeCount=len(pool_sizes),
            pPoolSizes=pool_sizes,
        )
        self.descriptor_pool = vk.vkCreateDescriptorPool(self.device, pool_info, None)
        alloc_info = vk.VkDescriptorSetAllocateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO,
            descriptorPool=self.descriptor_pool,
            descriptorSetCount=2,
            pSetLayouts=[self.descriptor_set_layout, self.descriptor_set_layout],
        )
        descriptor_sets = vk.vkAllocateDescriptorSets(self.device, alloc_info)
        self.descriptor_sets = [descriptor_sets[0], descriptor_sets[1]]

        pool_info = vk.VkCommandPoolCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,
            queueFamilyIndex=self.queue_family_index,
            flags=vk.VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT,
        )
        self.command_pool = vk.vkCreateCommandPool(self.device, pool_info, None)
        alloc_info = vk.VkCommandBufferAllocateInfo(
            sType=vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,
            commandPool=self.command_pool,
            level=vk.VK_COMMAND_BUFFER_LEVEL_PRIMARY,
            commandBufferCount=1,
        )
        self.command_buffer = vk.vkAllocateCommandBuffers(self.device, alloc_info)[0]

    def _create_storage_buffer(self, nbytes: int) -> tuple[object, object]:
        return self.gpu_vulkan_dispatcher._create_buffer(
            self.device,
            self.mem_props,
            nbytes,
            self.vk.VK_BUFFER_USAGE_STORAGE_BUFFER_BIT,
            self.gpu_vulkan_dispatcher.HOST_VISIBLE_COHERENT,
        )

    def _update_descriptor_set(self, descriptor_set: object, bindings: list[tuple[object, int]]) -> None:
        write_sets = []
        for binding, (buffer, nbytes) in enumerate(bindings):
            write_sets.append(
                self.vk.VkWriteDescriptorSet(
                    sType=self.vk.VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,
                    dstSet=descriptor_set,
                    dstBinding=binding,
                    descriptorCount=1,
                    descriptorType=self.vk.VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,
                    pBufferInfo=[
                        self.vk.VkDescriptorBufferInfo(buffer=buffer, offset=0, range=nbytes)
                    ],
                )
            )
        self.vk.vkUpdateDescriptorSets(self.device, len(write_sets), write_sets, 0, None)

    def _make_push_data(self, prime_count: int, rule_count: int, state_count: int):
        if hasattr(self.vk, "ffi"):
            return self.vk.ffi.new(
                "uint32_t[]", [int(prime_count), int(rule_count), int(state_count)]
            )
        return (ctypes.c_uint32 * 3)(prime_count, rule_count, state_count)

    def _record_dispatch_sequence(
        self,
        descriptor_sets: list[object],
        prime_count: int,
        rule_count: int,
        state_count: int,
        dispatch_count: int,
    ) -> None:
        begin_info = self.vk.VkCommandBufferBeginInfo(
            sType=self.vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
            flags=self.vk.VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
        )
        self.vk.vkBeginCommandBuffer(self.command_buffer, begin_info)
        self.vk.vkCmdBindPipeline(
            self.command_buffer, self.vk.VK_PIPELINE_BIND_POINT_COMPUTE, self.pipeline
        )
        groups = (state_count + 63) // 64
        push_data = self._make_push_data(prime_count, rule_count, state_count)
        memory_barrier = self.vk.VkMemoryBarrier(
            sType=self.vk.VK_STRUCTURE_TYPE_MEMORY_BARRIER,
            srcAccessMask=self.vk.VK_ACCESS_SHADER_WRITE_BIT,
            dstAccessMask=self.vk.VK_ACCESS_SHADER_READ_BIT | self.vk.VK_ACCESS_SHADER_WRITE_BIT,
        )
        for dispatch_ix in range(dispatch_count):
            descriptor_set = descriptor_sets[dispatch_ix % len(descriptor_sets)]
            self.vk.vkCmdBindDescriptorSets(
                self.command_buffer,
                self.vk.VK_PIPELINE_BIND_POINT_COMPUTE,
                self.pipeline_layout,
                0,
                1,
                [descriptor_set],
                0,
                None,
            )
            self.vk.vkCmdPushConstants(
                self.command_buffer,
                self.pipeline_layout,
                self.vk.VK_SHADER_STAGE_COMPUTE_BIT,
                0,
                12,
                push_data,
            )
            self.vk.vkCmdDispatch(self.command_buffer, groups, 1, 1)
            if dispatch_ix + 1 < dispatch_count:
                self.vk.vkCmdPipelineBarrier(
                    self.command_buffer,
                    self.vk.VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                    self.vk.VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                    0,
                    1,
                    [memory_barrier],
                    0,
                    None,
                    0,
                    None,
                )
        self.vk.vkEndCommandBuffer(self.command_buffer)

    def _submit_and_wait(self) -> None:
        submit_info = self.vk.VkSubmitInfo(
            sType=self.vk.VK_STRUCTURE_TYPE_SUBMIT_INFO,
            commandBufferCount=1,
            pCommandBuffers=[self.command_buffer],
        )
        fence = self.vk.vkCreateFence(
            self.device,
            self.vk.VkFenceCreateInfo(sType=self.vk.VK_STRUCTURE_TYPE_FENCE_CREATE_INFO),
            None,
        )
        self.vk.vkQueueSubmit(self.queue, 1, [submit_info], fence)
        self.vk.vkWaitForFences(self.device, 1, [fence], self.vk.VK_TRUE, 1_000_000_000)
        self.vk.vkDestroyFence(self.device, fence, None)
        self.vk.vkResetCommandBuffer(self.command_buffer, 0)

    def run_steps_batch_profiled(
        self, layout: CompiledFractranLayout, states: np.ndarray, steps: int
    ) -> FractranBatchProfiledResult:
        buffers = layout.gpu_buffers()
        state_matrix = np.asarray(states, dtype=np.int32, order="C")
        if state_matrix.ndim == 1:
            state_matrix = state_matrix.reshape(1, -1)
        if state_matrix.ndim != 2:
            raise ValueError("states must be a 1D or 2D exponent array")
        if state_matrix.shape[1] != layout.primes.shape[0]:
            raise ValueError("state prime dimension does not match compiled layout")
        if steps < 0:
            raise ValueError("steps must be non-negative")
        state_count, prime_count = state_matrix.shape
        total_start = time.perf_counter()
        host_prepare_start = total_start
        state_in = state_matrix.reshape(-1).copy()
        state_out = np.zeros_like(state_in)
        meta_out = np.zeros(state_count * 2, dtype=np.int32)
        den_thresholds = np.asarray(buffers["den_thresholds"], dtype=np.int32, order="C").reshape(-1)
        deltas = np.asarray(buffers["deltas"], dtype=np.int32, order="C").reshape(-1)
        required_masks = np.asarray(buffers["required_masks"], dtype=np.uint32, order="C")
        host_prepare_end = time.perf_counter()

        allocated: list[tuple[object, object]] = []
        try:
            allocate_start = time.perf_counter()
            den_buffer, den_memory = self._create_storage_buffer(den_thresholds.nbytes)
            delta_buffer, delta_memory = self._create_storage_buffer(deltas.nbytes)
            mask_buffer, mask_memory = self._create_storage_buffer(required_masks.nbytes)
            state_a_buffer, state_a_memory = self._create_storage_buffer(state_in.nbytes)
            state_b_buffer, state_b_memory = self._create_storage_buffer(state_out.nbytes)
            meta_buffer, meta_memory = self._create_storage_buffer(meta_out.nbytes)
            allocated.extend(
                [
                    (den_buffer, den_memory),
                    (delta_buffer, delta_memory),
                    (mask_buffer, mask_memory),
                    (state_a_buffer, state_a_memory),
                    (state_b_buffer, state_b_memory),
                    (meta_buffer, meta_memory),
                ]
            )
            allocate_end = time.perf_counter()

            upload_start = time.perf_counter()
            self.gpu_vulkan_dispatcher._write_buffer(self.device, den_memory, den_thresholds)
            self.gpu_vulkan_dispatcher._write_buffer(self.device, delta_memory, deltas)
            self.gpu_vulkan_dispatcher._write_buffer(self.device, mask_memory, required_masks)
            self.gpu_vulkan_dispatcher._write_buffer(self.device, state_a_memory, state_in)
            upload_end = time.perf_counter()

            descriptor_start = time.perf_counter()
            self._update_descriptor_set(
                self.descriptor_sets[0],
                [
                    (state_a_buffer, state_in.nbytes),
                    (den_buffer, den_thresholds.nbytes),
                    (delta_buffer, deltas.nbytes),
                    (mask_buffer, required_masks.nbytes),
                    (state_b_buffer, state_out.nbytes),
                    (meta_buffer, meta_out.nbytes),
                ],
            )
            self._update_descriptor_set(
                self.descriptor_sets[1],
                [
                    (state_b_buffer, state_out.nbytes),
                    (den_buffer, den_thresholds.nbytes),
                    (delta_buffer, deltas.nbytes),
                    (mask_buffer, required_masks.nbytes),
                    (state_a_buffer, state_in.nbytes),
                    (meta_buffer, meta_out.nbytes),
                ],
            )
            descriptor_end = time.perf_counter()

            current_shape = state_out.shape

            if steps == 0:
                record_end = descriptor_end
                execute_end = descriptor_end
                next_state = state_in
                meta = np.full(meta_out.shape, -1, dtype=np.int32)
                meta[1::2] = 0
            else:
                record_start = time.perf_counter()
                self._record_dispatch_sequence(
                    self.descriptor_sets, prime_count, len(layout.rules), state_count, steps
                )
                record_end = time.perf_counter()
                execute_start = time.perf_counter()
                self._submit_and_wait()
                execute_end = time.perf_counter()
                final_memory = state_b_memory if steps % 2 == 1 else state_a_memory
                readback_start = time.perf_counter()
                next_state = self.gpu_vulkan_dispatcher._read_buffer(
                    self.device, final_memory, current_shape, state_out.dtype
                )
                meta = self.gpu_vulkan_dispatcher._read_buffer(
                    self.device, meta_memory, meta_out.shape, meta_out.dtype
                )
                readback_end = time.perf_counter()
            if steps == 0:
                readback_start = execute_end
                readback_end = execute_end
            next_state_matrix = np.asarray(next_state, dtype=np.int32).reshape(state_count, prime_count)
            meta_matrix = np.asarray(meta, dtype=np.int32).reshape(state_count, 2)
            total_end = time.perf_counter()
            return FractranBatchProfiledResult(
                next_exponents=next_state_matrix,
                selected_rules=meta_matrix[:, 0].astype(np.int32, copy=False),
                halted=meta_matrix[:, 1].astype(bool, copy=False),
                phase_seconds={
                    "host_prepare": host_prepare_end - host_prepare_start,
                    "buffer_allocate": allocate_end - allocate_start,
                    "buffer_upload": upload_end - upload_start,
                    "descriptor_update": descriptor_end - descriptor_start,
                    "command_record": record_end - descriptor_end if steps == 0 else record_end - record_start,
                    "submit_wait": execute_end - record_end if steps == 0 else execute_end - execute_start,
                    "readback": readback_end - readback_start,
                    "total": total_end - total_start,
                },
            )
        finally:
            for buffer, memory in allocated:
                self.handles.destroy_buffer(buffer, memory)

    def run_steps_batch(
        self, layout: CompiledFractranLayout, states: np.ndarray, steps: int
    ) -> FractranBatchStepResult:
        profiled = self.run_steps_batch_profiled(layout, states, steps)
        return FractranBatchStepResult(
            next_exponents=profiled.next_exponents,
            selected_rules=profiled.selected_rules,
            halted=profiled.halted,
        )

    def step_batch(self, layout: CompiledFractranLayout, states: np.ndarray) -> FractranBatchStepResult:
        return self.run_steps_batch(layout, states, 1)

    def step(self, layout: CompiledFractranLayout, state: np.ndarray) -> FractranStepResult:
        result = self.step_batch(layout, np.asarray(state, dtype=np.int32).reshape(1, -1))
        return FractranStepResult(
            next_exponents=result.next_exponents[0],
            selected_rule=int(result.selected_rules[0]),
            halted=bool(result.halted[0]),
        )

    def close(self) -> None:
        if getattr(self, "device", None) is None:
            return
        self.vk.vkDestroyCommandPool(self.device, self.command_pool, None)
        self.vk.vkDestroyDescriptorPool(self.device, self.descriptor_pool, None)
        self.vk.vkDestroyPipeline(self.device, self.pipeline, None)
        self.vk.vkDestroyPipelineLayout(self.device, self.pipeline_layout, None)
        self.vk.vkDestroyShaderModule(self.device, self.shader_module, None)
        self.vk.vkDestroyDescriptorSetLayout(self.device, self.descriptor_set_layout, None)
        self.handles.close()
        self.device = None

    def __enter__(self) -> "VulkanFractranStepper":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
