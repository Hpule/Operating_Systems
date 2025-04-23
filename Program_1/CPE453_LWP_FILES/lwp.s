	.file	"lwp.c"
	.comm	lwp_ptable,960,32
	.globl	lwp_processes
	.bss
	.align 4
	.type	lwp_processes, @object
	.size	lwp_processes, 4
lwp_processes:
	.zero	4
	.globl	curr_process
	.data
	.align 4
	.type	curr_process, @object
	.size	curr_process, 4
curr_process:
	.long	-1
	.globl	curr_pid_process
	.bss
	.align 8
	.type	curr_pid_process, @object
	.size	curr_pid_process, 8
curr_pid_process:
	.zero	8
	.globl	global_sp
	.align 8
	.type	global_sp, @object
	.size	global_sp, 8
global_sp:
	.zero	8
	.globl	scheduler_function
	.align 8
	.type	scheduler_function, @object
	.size	scheduler_function, 8
scheduler_function:
	.zero	8
	.text
	.globl	ribbed_robin
	.type	ribbed_robin, @function
ribbed_robin:
.LFB2:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	movl	lwp_processes(%rip), %eax
	leal	-1(%rax), %edx
	movl	curr_process(%rip), %eax
	cmpl	%eax, %edx
	jne	.L2
	movl	$0, curr_process(%rip)
	jmp	.L1
.L2:
	movl	curr_process(%rip), %eax
	addl	$1, %eax
	movl	%eax, curr_process(%rip)
.L1:
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE2:
	.size	ribbed_robin, .-ribbed_robin
	.globl	based_scheduler
	.type	based_scheduler, @function
based_scheduler:
.LFB3:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	movq	scheduler_function(%rip), %rax
	testq	%rax, %rax
	jne	.L5
	movl	$0, %eax
	call	ribbed_robin
	jmp	.L4
.L5:
	movq	scheduler_function(%rip), %rax
	call	*%rax
	movl	%eax, curr_process(%rip)
.L4:
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE3:
	.size	based_scheduler, .-based_scheduler
	.globl	new_lwp
	.type	new_lwp, @function
new_lwp:
.LFB4:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	subq	$48, %rsp
	movq	%rdi, -24(%rbp)
	movq	%rsi, -32(%rbp)
	movq	%rdx, -40(%rbp)
	movl	lwp_processes(%rip), %eax
	cmpl	$29, %eax
	jle	.L8
	movl	$-1, %eax
	jmp	.L9
.L8:
	movq	-40(%rbp), %rax
	salq	$2, %rax
	movq	%rax, %rdi
	call	malloc
	movq	%rax, -8(%rbp)
	movl	lwp_processes(%rip), %eax
	cltq
	salq	$5, %rax
	leaq	lwp_ptable(%rax), %rdx
	movq	-8(%rbp), %rax
	movq	%rax, 8(%rdx)
	movq	-40(%rbp), %rax
	salq	$3, %rax
	addq	%rax, -8(%rbp)
	subq	$8, -8(%rbp)
	movq	-32(%rbp), %rdx
	movq	-8(%rbp), %rax
	movq	%rdx, (%rax)
	subq	$8, -8(%rbp)
	movl	$lwp_exit, %edx
	movq	-8(%rbp), %rax
	movq	%rdx, (%rax)
	subq	$8, -8(%rbp)
	movq	-24(%rbp), %rdx
	movq	-8(%rbp), %rax
	movq	%rdx, (%rax)
	subq	$8, -8(%rbp)
	movq	-8(%rbp), %rax
	movl	$4276993775, %ecx
	movq	%rcx, (%rax)
	movq	-8(%rbp), %rax
	movq	%rax, -16(%rbp)
	subq	$56, -8(%rbp)
	movq	-8(%rbp), %rax
	movq	-16(%rbp), %rdx
	movq	%rdx, (%rax)
	movq	curr_pid_process(%rip), %rax
	addq	$1, %rax
	movq	%rax, curr_pid_process(%rip)
	movl	lwp_processes(%rip), %edx
	movq	curr_pid_process(%rip), %rax
	movslq	%edx, %rdx
	salq	$5, %rdx
	addq	$lwp_ptable, %rdx
	movq	%rax, (%rdx)
	movl	lwp_processes(%rip), %eax
	cltq
	salq	$5, %rax
	leaq	lwp_ptable+16(%rax), %rdx
	movq	-8(%rbp), %rax
	movq	%rax, 8(%rdx)
	movl	lwp_processes(%rip), %eax
	cltq
	salq	$5, %rax
	leaq	lwp_ptable+16(%rax), %rdx
	movq	-40(%rbp), %rax
	movq	%rax, (%rdx)
	movl	lwp_processes(%rip), %eax
	addl	$1, %eax
	movl	%eax, lwp_processes(%rip)
	movl	lwp_processes(%rip), %eax
	subl	$1, %eax
	cltq
	salq	$5, %rax
	addq	$lwp_ptable, %rax
	movq	(%rax), %rax
.L9:
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE4:
	.size	new_lwp, .-new_lwp
	.globl	lwp_getpid
	.type	lwp_getpid, @function
lwp_getpid:
.LFB5:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	movl	curr_process(%rip), %eax
	cmpl	$-1, %eax
	jne	.L11
	movl	$0, %eax
	jmp	.L12
.L11:
	movl	curr_process(%rip), %eax
	cltq
	salq	$5, %rax
	addq	$lwp_ptable, %rax
	movq	(%rax), %rax
.L12:
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE5:
	.size	lwp_getpid, .-lwp_getpid
	.globl	lwp_yield
	.type	lwp_yield, @function
lwp_yield:
.LFB6:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
#APP
# 101 "lwp.c" 1
	pushq %rax
# 0 "" 2
# 101 "lwp.c" 1
	pushq %rbx
# 0 "" 2
# 101 "lwp.c" 1
	pushq %rcx
# 0 "" 2
# 101 "lwp.c" 1
	pushq %rdx
# 0 "" 2
# 101 "lwp.c" 1
	pushq %rsi
# 0 "" 2
# 101 "lwp.c" 1
	pushq %rdi
# 0 "" 2
# 101 "lwp.c" 1
	pushq %r8
# 0 "" 2
# 101 "lwp.c" 1
	pushq %r9
# 0 "" 2
# 101 "lwp.c" 1
	pushq %r10
# 0 "" 2
# 101 "lwp.c" 1
	pushq %r11
# 0 "" 2
# 101 "lwp.c" 1
	pushq %r12
# 0 "" 2
# 101 "lwp.c" 1
	pushq %r13
# 0 "" 2
# 101 "lwp.c" 1
	pushq %r14
# 0 "" 2
# 101 "lwp.c" 1
	pushq %r15
# 0 "" 2
# 101 "lwp.c" 1
	pushq %rbp
# 0 "" 2
#NO_APP
	movl	curr_process(%rip), %edx
#APP
# 102 "lwp.c" 1
	movq  %rsp,%rax
# 0 "" 2
#NO_APP
	movslq	%edx, %rdx
	salq	$5, %rdx
	addq	$lwp_ptable+16, %rdx
	movq	%rax, 8(%rdx)
	movl	$0, %eax
	call	based_scheduler
	movl	curr_process(%rip), %eax
	cltq
	salq	$5, %rax
	addq	$lwp_ptable+16, %rax
	movq	8(%rax), %rax
#APP
# 106 "lwp.c" 1
	movq  %rax,%rsp
# 0 "" 2
# 107 "lwp.c" 1
	popq  %rbp
# 0 "" 2
# 107 "lwp.c" 1
	popq  %r15
# 0 "" 2
# 107 "lwp.c" 1
	popq  %r14
# 0 "" 2
# 107 "lwp.c" 1
	popq  %r13
# 0 "" 2
# 107 "lwp.c" 1
	popq  %r12
# 0 "" 2
# 107 "lwp.c" 1
	popq  %r11
# 0 "" 2
# 107 "lwp.c" 1
	popq  %r10
# 0 "" 2
# 107 "lwp.c" 1
	popq  %r9
# 0 "" 2
# 107 "lwp.c" 1
	popq  %r8
# 0 "" 2
# 107 "lwp.c" 1
	popq  %rdi
# 0 "" 2
# 107 "lwp.c" 1
	popq  %rsi
# 0 "" 2
# 107 "lwp.c" 1
	popq  %rdx
# 0 "" 2
# 107 "lwp.c" 1
	popq  %rcx
# 0 "" 2
# 107 "lwp.c" 1
	popq  %rbx
# 0 "" 2
# 107 "lwp.c" 1
	popq  %rax
# 0 "" 2
# 107 "lwp.c" 1
	movq  %rbp,%rsp
# 0 "" 2
#NO_APP
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE6:
	.size	lwp_yield, .-lwp_yield
	.globl	lwp_exit
	.type	lwp_exit, @function
lwp_exit:
.LFB7:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	subq	$16, %rsp
	movl	curr_process(%rip), %eax
	cltq
	salq	$5, %rax
	addq	$lwp_ptable, %rax
	movq	8(%rax), %rax
	movq	%rax, %rdi
	call	free
	movl	lwp_processes(%rip), %eax
	subl	$1, %eax
	movl	%eax, lwp_processes(%rip)
	movl	lwp_processes(%rip), %eax
	testl	%eax, %eax
	jle	.L15
	movl	$0, -4(%rbp)
	movl	curr_process(%rip), %eax
	movl	%eax, -4(%rbp)
	jmp	.L16
.L17:
	movl	-4(%rbp), %eax
	leal	1(%rax), %edx
	movl	-4(%rbp), %eax
	cltq
	salq	$5, %rax
	addq	$lwp_ptable, %rax
	movslq	%edx, %rdx
	salq	$5, %rdx
	addq	$lwp_ptable, %rdx
	movq	(%rdx), %rcx
	movq	%rcx, (%rax)
	movq	8(%rdx), %rcx
	movq	%rcx, 8(%rax)
	movq	16(%rdx), %rcx
	movq	%rcx, 16(%rax)
	movq	24(%rdx), %rdx
	movq	%rdx, 24(%rax)
	addl	$1, -4(%rbp)
.L16:
	movl	lwp_processes(%rip), %eax
	cmpl	%eax, -4(%rbp)
	jl	.L17
	movl	curr_process(%rip), %eax
	cltq
	salq	$5, %rax
	addq	$lwp_ptable+16, %rax
	movq	8(%rax), %rax
#APP
# 126 "lwp.c" 1
	movq  %rax,%rsp
# 0 "" 2
# 127 "lwp.c" 1
	popq  %rbp
# 0 "" 2
# 127 "lwp.c" 1
	popq  %r15
# 0 "" 2
# 127 "lwp.c" 1
	popq  %r14
# 0 "" 2
# 127 "lwp.c" 1
	popq  %r13
# 0 "" 2
# 127 "lwp.c" 1
	popq  %r12
# 0 "" 2
# 127 "lwp.c" 1
	popq  %r11
# 0 "" 2
# 127 "lwp.c" 1
	popq  %r10
# 0 "" 2
# 127 "lwp.c" 1
	popq  %r9
# 0 "" 2
# 127 "lwp.c" 1
	popq  %r8
# 0 "" 2
# 127 "lwp.c" 1
	popq  %rdi
# 0 "" 2
# 127 "lwp.c" 1
	popq  %rsi
# 0 "" 2
# 127 "lwp.c" 1
	popq  %rdx
# 0 "" 2
# 127 "lwp.c" 1
	popq  %rcx
# 0 "" 2
# 127 "lwp.c" 1
	popq  %rbx
# 0 "" 2
# 127 "lwp.c" 1
	popq  %rax
# 0 "" 2
# 127 "lwp.c" 1
	movq  %rbp,%rsp
# 0 "" 2
#NO_APP
	jmp	.L14
.L15:
	movq	global_sp(%rip), %rax
#APP
# 121 "lwp.c" 1
	movq  %rax,%rsp
# 0 "" 2
# 122 "lwp.c" 1
	popq  %rbp
# 0 "" 2
# 122 "lwp.c" 1
	popq  %r15
# 0 "" 2
# 122 "lwp.c" 1
	popq  %r14
# 0 "" 2
# 122 "lwp.c" 1
	popq  %r13
# 0 "" 2
# 122 "lwp.c" 1
	popq  %r12
# 0 "" 2
# 122 "lwp.c" 1
	popq  %r11
# 0 "" 2
# 122 "lwp.c" 1
	popq  %r10
# 0 "" 2
# 122 "lwp.c" 1
	popq  %r9
# 0 "" 2
# 122 "lwp.c" 1
	popq  %r8
# 0 "" 2
# 122 "lwp.c" 1
	popq  %rdi
# 0 "" 2
# 122 "lwp.c" 1
	popq  %rsi
# 0 "" 2
# 122 "lwp.c" 1
	popq  %rdx
# 0 "" 2
# 122 "lwp.c" 1
	popq  %rcx
# 0 "" 2
# 122 "lwp.c" 1
	popq  %rbx
# 0 "" 2
# 122 "lwp.c" 1
	popq  %rax
# 0 "" 2
# 122 "lwp.c" 1
	movq  %rbp,%rsp
# 0 "" 2
#NO_APP
	nop
.L14:
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE7:
	.size	lwp_exit, .-lwp_exit
	.globl	lwp_start
	.type	lwp_start, @function
lwp_start:
.LFB8:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	movl	lwp_processes(%rip), %eax
	testl	%eax, %eax
	jg	.L21
	jmp	.L20
.L21:
#APP
# 139 "lwp.c" 1
	pushq %rax
# 0 "" 2
# 139 "lwp.c" 1
	pushq %rbx
# 0 "" 2
# 139 "lwp.c" 1
	pushq %rcx
# 0 "" 2
# 139 "lwp.c" 1
	pushq %rdx
# 0 "" 2
# 139 "lwp.c" 1
	pushq %rsi
# 0 "" 2
# 139 "lwp.c" 1
	pushq %rdi
# 0 "" 2
# 139 "lwp.c" 1
	pushq %r8
# 0 "" 2
# 139 "lwp.c" 1
	pushq %r9
# 0 "" 2
# 139 "lwp.c" 1
	pushq %r10
# 0 "" 2
# 139 "lwp.c" 1
	pushq %r11
# 0 "" 2
# 139 "lwp.c" 1
	pushq %r12
# 0 "" 2
# 139 "lwp.c" 1
	pushq %r13
# 0 "" 2
# 139 "lwp.c" 1
	pushq %r14
# 0 "" 2
# 139 "lwp.c" 1
	pushq %r15
# 0 "" 2
# 139 "lwp.c" 1
	pushq %rbp
# 0 "" 2
# 142 "lwp.c" 1
	movq  %rsp,%rax
# 0 "" 2
#NO_APP
	movq	%rax, global_sp(%rip)
	movl	$0, curr_process(%rip)
	movl	curr_process(%rip), %eax
	cltq
	salq	$5, %rax
	addq	$lwp_ptable+16, %rax
	movq	8(%rax), %rax
#APP
# 148 "lwp.c" 1
	movq  %rax,%rsp
# 0 "" 2
# 151 "lwp.c" 1
	popq  %rbp
# 0 "" 2
# 151 "lwp.c" 1
	popq  %r15
# 0 "" 2
# 151 "lwp.c" 1
	popq  %r14
# 0 "" 2
# 151 "lwp.c" 1
	popq  %r13
# 0 "" 2
# 151 "lwp.c" 1
	popq  %r12
# 0 "" 2
# 151 "lwp.c" 1
	popq  %r11
# 0 "" 2
# 151 "lwp.c" 1
	popq  %r10
# 0 "" 2
# 151 "lwp.c" 1
	popq  %r9
# 0 "" 2
# 151 "lwp.c" 1
	popq  %r8
# 0 "" 2
# 151 "lwp.c" 1
	popq  %rdi
# 0 "" 2
# 151 "lwp.c" 1
	popq  %rsi
# 0 "" 2
# 151 "lwp.c" 1
	popq  %rdx
# 0 "" 2
# 151 "lwp.c" 1
	popq  %rcx
# 0 "" 2
# 151 "lwp.c" 1
	popq  %rbx
# 0 "" 2
# 151 "lwp.c" 1
	popq  %rax
# 0 "" 2
# 151 "lwp.c" 1
	movq  %rbp,%rsp
# 0 "" 2
#NO_APP
.L20:
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE8:
	.size	lwp_start, .-lwp_start
	.globl	lwp_stop
	.type	lwp_stop, @function
lwp_stop:
.LFB9:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
#APP
# 156 "lwp.c" 1
	pushq %rax
# 0 "" 2
# 156 "lwp.c" 1
	pushq %rbx
# 0 "" 2
# 156 "lwp.c" 1
	pushq %rcx
# 0 "" 2
# 156 "lwp.c" 1
	pushq %rdx
# 0 "" 2
# 156 "lwp.c" 1
	pushq %rsi
# 0 "" 2
# 156 "lwp.c" 1
	pushq %rdi
# 0 "" 2
# 156 "lwp.c" 1
	pushq %r8
# 0 "" 2
# 156 "lwp.c" 1
	pushq %r9
# 0 "" 2
# 156 "lwp.c" 1
	pushq %r10
# 0 "" 2
# 156 "lwp.c" 1
	pushq %r11
# 0 "" 2
# 156 "lwp.c" 1
	pushq %r12
# 0 "" 2
# 156 "lwp.c" 1
	pushq %r13
# 0 "" 2
# 156 "lwp.c" 1
	pushq %r14
# 0 "" 2
# 156 "lwp.c" 1
	pushq %r15
# 0 "" 2
# 156 "lwp.c" 1
	pushq %rbp
# 0 "" 2
#NO_APP
	movl	curr_process(%rip), %edx
#APP
# 158 "lwp.c" 1
	movq  %rsp,%rax
# 0 "" 2
#NO_APP
	movslq	%edx, %rdx
	salq	$5, %rdx
	addq	$lwp_ptable+16, %rdx
	movq	%rax, 8(%rdx)
	movq	global_sp(%rip), %rax
#APP
# 159 "lwp.c" 1
	movq  %rax,%rsp
# 0 "" 2
# 161 "lwp.c" 1
	popq  %rbp
# 0 "" 2
# 161 "lwp.c" 1
	popq  %r15
# 0 "" 2
# 161 "lwp.c" 1
	popq  %r14
# 0 "" 2
# 161 "lwp.c" 1
	popq  %r13
# 0 "" 2
# 161 "lwp.c" 1
	popq  %r12
# 0 "" 2
# 161 "lwp.c" 1
	popq  %r11
# 0 "" 2
# 161 "lwp.c" 1
	popq  %r10
# 0 "" 2
# 161 "lwp.c" 1
	popq  %r9
# 0 "" 2
# 161 "lwp.c" 1
	popq  %r8
# 0 "" 2
# 161 "lwp.c" 1
	popq  %rdi
# 0 "" 2
# 161 "lwp.c" 1
	popq  %rsi
# 0 "" 2
# 161 "lwp.c" 1
	popq  %rdx
# 0 "" 2
# 161 "lwp.c" 1
	popq  %rcx
# 0 "" 2
# 161 "lwp.c" 1
	popq  %rbx
# 0 "" 2
# 161 "lwp.c" 1
	popq  %rax
# 0 "" 2
# 161 "lwp.c" 1
	movq  %rbp,%rsp
# 0 "" 2
#NO_APP
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE9:
	.size	lwp_stop, .-lwp_stop
	.globl	lwp_set_scheduler
	.type	lwp_set_scheduler, @function
lwp_set_scheduler:
.LFB10:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	movq	%rdi, -8(%rbp)
	movq	-8(%rbp), %rax
	movq	%rax, scheduler_function(%rip)
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE10:
	.size	lwp_set_scheduler, .-lwp_set_scheduler
	.ident	"GCC: (GNU) 4.8.5 20150623 (Red Hat 4.8.5-44)"
	.section	.note.GNU-stack,"",@progbits
