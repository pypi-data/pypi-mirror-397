#!/bin/bash

# PIDS 泄露诊断脚本
# 深入分析容器内的进程情况

set -e

CONTAINER_NAME="snail-job-executor"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}========================================="
echo "🔬 PIDS 泄露深度诊断"
echo "==========================================${NC}"
echo ""

# 检查容器是否运行
if ! docker ps | grep -q $CONTAINER_NAME; then
    echo -e "${RED}❌ 容器未运行${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 容器正在运行${NC}"
echo ""

# ==================== 1. 总体进程统计 ====================
echo -e "${CYAN}========================================="
echo "📊 1. 总体进程统计"
echo "==========================================${NC}"

TOTAL_PIDS=$(docker exec $CONTAINER_NAME ps aux 2>/dev/null | wc -l)
echo -e "${YELLOW}总进程数 (PIDS): ${TOTAL_PIDS}${NC}"
echo ""

# ==================== 2. 按进程类型分类 ====================
echo -e "${CYAN}========================================="
echo "📂 2. 进程类型分类统计"
echo "==========================================${NC}"

echo "正在分析进程..."
docker exec $CONTAINER_NAME bash -c '
ps aux | awk "NR>1 {print \$11}" | sort | uniq -c | sort -rn | head -20
' > /tmp/pid_analysis.txt

cat /tmp/pid_analysis.txt | while read line; do
    COUNT=$(echo $line | awk '{print $1}')
    CMD=$(echo $line | awk '{$1=""; print $0}' | sed 's/^ //')
    
    if [ "$COUNT" -gt 10 ]; then
        COLOR=$RED
    elif [ "$COUNT" -gt 5 ]; then
        COLOR=$YELLOW
    else
        COLOR=$GREEN
    fi
    
    echo -e "${COLOR}${COUNT}${NC} 个进程: ${CMD}"
done

echo ""

# ==================== 3. Python 进程详情 ====================
echo -e "${CYAN}========================================="
echo "🐍 3. Python 进程详情"
echo "==========================================${NC}"

PYTHON_COUNT=$(docker exec $CONTAINER_NAME ps aux | grep -c "[p]ython" || true)
echo -e "${YELLOW}Python 进程总数: ${PYTHON_COUNT}${NC}"
echo ""

echo "Python 进程列表:"
docker exec $CONTAINER_NAME ps aux | grep "[p]ython" | head -20 || echo "无 Python 进程"
echo ""

# ==================== 4. Git 进程详情 ====================
echo -e "${CYAN}========================================="
echo "📦 4. Git 进程详情"
echo "==========================================${NC}"

GIT_COUNT=$(docker exec $CONTAINER_NAME ps aux | grep -c "[g]it" || true)
echo -e "${YELLOW}Git 进程总数: ${GIT_COUNT}${NC}"

if [ "$GIT_COUNT" -gt 0 ]; then
    echo -e "${RED}⚠️  发现 Git 进程，可能存在 Git 操作未完成或卡死${NC}"
    echo ""
    echo "Git 进程列表:"
    docker exec $CONTAINER_NAME ps aux | grep "[g]it" || true
else
    echo -e "${GREEN}✅ 无 Git 进程${NC}"
fi
echo ""

# ==================== 5. 僵尸进程检查 ====================
echo -e "${CYAN}========================================="
echo "👻 5. 僵尸进程检查"
echo "==========================================${NC}"

ZOMBIE_COUNT=$(docker exec $CONTAINER_NAME ps aux | grep -c "[d]efunct" || true)
echo -e "${YELLOW}僵尸进程数: ${ZOMBIE_COUNT}${NC}"

if [ "$ZOMBIE_COUNT" -gt 0 ]; then
    echo -e "${RED}⚠️  发现僵尸进程！${NC}"
    echo ""
    echo "僵尸进程列表:"
    docker exec $CONTAINER_NAME ps aux | grep "[d]efunct" || true
    echo ""
    echo "僵尸进程的父进程:"
    docker exec $CONTAINER_NAME bash -c '
    ps aux | grep defunct | awk "{print \$2}" | while read pid; do
        ppid=$(ps -o ppid= -p $pid 2>/dev/null || echo "N/A")
        if [ "$ppid" != "N/A" ]; then
            echo "PID $pid -> PPID $ppid"
            ps aux | grep -E "^\w+\s+$ppid"
        fi
    done
    ' || true
else
    echo -e "${GREEN}✅ 无僵尸进程${NC}"
fi
echo ""

# ==================== 6. 线程统计 ====================
echo -e "${CYAN}========================================="
echo "🧵 6. 线程统计"
echo "==========================================${NC}"

echo "正在统计线程..."
docker exec $CONTAINER_NAME bash -c '
ps -eLf | wc -l
' > /tmp/thread_count.txt

THREAD_COUNT=$(cat /tmp/thread_count.txt)
echo -e "${YELLOW}总线程数: ${THREAD_COUNT}${NC}"
echo ""

# 按进程统计线程数
echo "线程数最多的前 10 个进程:"
docker exec $CONTAINER_NAME bash -c '
ps -eLf | awk "NR>1 {print \$4, \$5}" | sort | uniq -c | sort -rn | head -10
' | while read line; do
    COUNT=$(echo $line | awk '{print $1}')
    PID=$(echo $line | awk '{print $2}')
    
    if [ "$COUNT" -gt 50 ]; then
        COLOR=$RED
    elif [ "$COUNT" -gt 20 ]; then
        COLOR=$YELLOW
    else
        COLOR=$GREEN
    fi
    
    CMD=$(docker exec $CONTAINER_NAME ps -p $PID -o comm= 2>/dev/null || echo "N/A")
    echo -e "${COLOR}${COUNT}${NC} 个线程 | PID: ${PID} | 命令: ${CMD}"
done

echo ""

# ==================== 7. 子进程树 ====================
echo -e "${CYAN}========================================="
echo "🌳 7. 进程树"
echo "==========================================${NC}"

echo "主要进程树结构:"
docker exec $CONTAINER_NAME bash -c 'ps auxf | head -50' || true
echo ""

# ==================== 8. UV/UVicorn 进程 ====================
echo -e "${CYAN}========================================="
echo "⚡ 8. UV/Uvicorn 进程"
echo "==========================================${NC}"

UV_COUNT=$(docker exec $CONTAINER_NAME ps aux | grep -E "[u]v |[u]vicorn" | wc -l || true)
echo -e "${YELLOW}UV/Uvicorn 进程数: ${UV_COUNT}${NC}"

if [ "$UV_COUNT" -gt 0 ]; then
    docker exec $CONTAINER_NAME ps aux | grep -E "[u]v |[u]vicorn" || true
fi
echo ""

# ==================== 9. 长时间运行的进程 ====================
echo -e "${CYAN}========================================="
echo "⏰ 9. 长时间运行的进程 (TIME > 0:01)"
echo "==========================================${NC}"

docker exec $CONTAINER_NAME bash -c '
ps aux | awk "NR>1 {
    split(\$10, time, \":\");
    if ((time[1] > 0) || (time[2] > 1)) {
        print \$0
    }
}" | head -20
' || echo "无长时间运行的进程"

echo ""

# ==================== 10. 文件描述符统计 ====================
echo -e "${CYAN}========================================="
echo "📁 10. 文件描述符统计"
echo "==========================================${NC}"

echo "文件描述符最多的前 10 个进程:"
docker exec $CONTAINER_NAME bash -c '
for pid in $(ps aux | awk "NR>1 {print \$2}"); do
    fd_count=$(ls -la /proc/$pid/fd 2>/dev/null | wc -l || echo 0)
    if [ $fd_count -gt 10 ]; then
        cmd=$(ps -p $pid -o comm= 2>/dev/null || echo "N/A")
        echo "$fd_count $pid $cmd"
    fi
done | sort -rn | head -10
' | while read line; do
    FD_COUNT=$(echo $line | awk '{print $1}')
    PID=$(echo $line | awk '{print $2}')
    CMD=$(echo $line | awk '{$1=""; $2=""; print $0}' | sed 's/^ *//')
    
    if [ "$FD_COUNT" -gt 100 ]; then
        COLOR=$RED
    elif [ "$FD_COUNT" -gt 50 ]; then
        COLOR=$YELLOW
    else
        COLOR=$GREEN
    fi
    
    echo -e "${COLOR}${FD_COUNT}${NC} 个文件描述符 | PID: ${PID} | 命令: ${CMD}"
done

echo ""

# ==================== 11. 实时监控模式 ====================
echo -e "${CYAN}========================================="
echo "📊 11. 实时监控 (30秒)"
echo "==========================================${NC}"

echo "观察 PIDS 变化趋势..."
echo ""

INITIAL=$(docker exec $CONTAINER_NAME ps aux | wc -l)
echo -e "初始 PIDS: ${YELLOW}${INITIAL}${NC}"

for i in {1..20}; do
    sleep 15
    CURRENT=$(docker exec $CONTAINER_NAME ps aux | wc -l)
    CHANGE=$((CURRENT - INITIAL))
    
    if [ $CHANGE -gt 5 ]; then
        COLOR=$RED
        EMOJI="🔴"
    elif [ $CHANGE -gt 2 ]; then
        COLOR=$YELLOW
        EMOJI="🟡"
    elif [ $CHANGE -lt 0 ]; then
        COLOR=$GREEN
        EMOJI="🟢"
    else
        COLOR=$NC
        EMOJI="⚪"
    fi
    
    echo -e "${EMOJI} [${i}/20] PIDS: ${COLOR}${CURRENT}${NC} (变化: ${CHANGE})"
    
    # 如果增长明显，捕获新增进程
    if [ $CHANGE -gt 3 ]; then
        echo "   📸 捕获新增进程:"
        docker exec $CONTAINER_NAME ps aux | tail -n $((CHANGE + 5)) | head -$CHANGE
    fi
done

FINAL=$(docker exec $CONTAINER_NAME ps aux | wc -l)
TOTAL_CHANGE=$((FINAL - INITIAL))

echo ""
echo -e "最终 PIDS: ${YELLOW}${FINAL}${NC}"
echo -e "总变化: ${YELLOW}${TOTAL_CHANGE}${NC}"

echo ""

# ==================== 12. 诊断结果汇总 ====================
echo -e "${CYAN}========================================="
echo "🎯 诊断结果汇总"
echo "==========================================${NC}"

echo ""
echo -e "${BLUE}关键指标:${NC}"
echo "  - 总进程数: $TOTAL_PIDS"
echo "  - Python 进程: $PYTHON_COUNT"
echo "  - Git 进程: $GIT_COUNT"
echo "  - 僵尸进程: $ZOMBIE_COUNT"
echo "  - 线程数: $THREAD_COUNT"
echo "  - 30秒增长: $TOTAL_CHANGE"
echo ""

# 判断问题类型
echo -e "${BLUE}可能的问题:${NC}"

if [ "$GIT_COUNT" -gt 5 ]; then
    echo -e "${RED}  ⚠️  Git 进程过多 ($GIT_COUNT)${NC}"
    echo "      → Git 操作可能卡死或未正确清理"
    echo "      → 检查 Git 缓存是否生效"
fi

if [ "$ZOMBIE_COUNT" -gt 0 ]; then
    echo -e "${RED}  ⚠️  存在僵尸进程 ($ZOMBIE_COUNT)${NC}"
    echo "      → 子进程未正确回收"
    echo "      → 检查 subprocess.wait() 调用"
fi

if [ "$PYTHON_COUNT" -gt 50 ]; then
    echo -e "${RED}  ⚠️  Python 进程过多 ($PYTHON_COUNT)${NC}"
    echo "      → 可能存在线程或进程泄露"
    echo "      → 检查 threading.Thread 和 asyncio 事件循环"
fi

if [ "$TOTAL_CHANGE" -gt 5 ]; then
    echo -e "${RED}  ⚠️  30秒内增长了 $TOTAL_CHANGE 个进程${NC}"
    echo "      → 进程持续增长，问题仍然存在"
    echo "      → 需要进一步调查"
elif [ "$TOTAL_CHANGE" -le 0 ]; then
    echo -e "${GREEN}  ✅ 30秒内进程数稳定或减少${NC}"
    echo "      → 清理机制正常工作"
else
    echo -e "${YELLOW}  ⚪ 30秒内轻微增长${NC}"
    echo "      → 继续观察"
fi

echo ""

# ==================== 13. 建议操作 ====================
echo -e "${CYAN}========================================="
echo "💡 建议操作"
echo "==========================================${NC}"

echo ""
echo "1. 查看详细进程信息:"
echo "   docker exec $CONTAINER_NAME ps auxf"
echo ""
echo "2. 查看 Git 缓存日志:"
echo "   docker logs $CONTAINER_NAME | grep '跳过.*缓存'"
echo ""
echo "3. 查看最近的错误日志:"
echo "   docker logs $CONTAINER_NAME --tail=100 | grep -i error"
echo ""
echo "4. 进入容器手动排查:"
echo "   docker exec -it $CONTAINER_NAME bash"
echo "   然后执行: ps auxf, top, htop"
echo ""
echo "5. 导出完整诊断结果:"
echo "   ./diagnose_pids.sh > diagnosis_$(date +%Y%m%d_%H%M%S).txt"
echo ""

echo -e "${CYAN}=========================================${NC}"
