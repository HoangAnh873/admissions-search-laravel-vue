<!-- src/components/backend/member/MemberGroupTable.vue -->
<script setup>
import { ref, computed } from 'vue'

// Props và Emits
const props = defineProps(['members', 'selectedMembers'])
const emit = defineEmits(['edit', 'delete', 'update:selectedMembers'])

// Xử lý chọn checkbox
const toggleSelect = (index) => {
    const newSelected = [...props.selectedMembers]
    const i = newSelected.indexOf(index)
    if (i > -1) newSelected.splice(i, 1)
    else newSelected.push(index)
    emit('update:selectedMembers', newSelected)
}

// Phân trang
const currentPage = ref(1)
const pageSize = 5
const paginatedMembers = computed(() => {
    const start = (currentPage.value - 1) * pageSize
    return props.members.slice(start, start + pageSize)
})


// Emit hành động edit / delete (dùng index toàn cục)
const editMember = (index) => {
    emit('edit', index + (currentPage.value - 1) * pageSize)
}

const deleteMember = (index) => {
    emit('delete', index + (currentPage.value - 1) * pageSize)
}
</script>

<template>
    <table class="table">
        <thead>
            <tr>
                <th></th>
                <th>Tên nhóm thành viên</th>
                <th>Số thành viên</th>
                <th>Mô tả</th>
                <th>Trạng thái</th>
                <th>Thao tác</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(member, i) in paginatedMembers" :key="i">
                <td>
                    <input 
                        type="checkbox" 
                        :value="i + (currentPage - 1) * pageSize"
                        :checked="props.selectedMembers.includes(i + (currentPage - 1) * pageSize)"
                        @change="toggleSelect(i + (currentPage - 1) * pageSize)"
                    />
                </td>
                <td>{{ member.name }}</td>
                <td>{{ member.quantity }}</td>
                <td>{{ member.role }}</td>
                <td>{{ member.status }}</td>
                <td>
                    <button @click="editMember(i)" class="btn btn-primary">
                        <i class="bx bx-edit"></i>
                    </button>
                    <button @click="deleteMember(i)" class="btn btn-danger">
                        <i class="bx bx-trash"></i>
                    </button>
                </td>
            </tr>
        </tbody>
    </table>
</template>
