let chart;
let entropyHistory = [];
let running = false;
let interval;

// 初始化图表
function initChart() {
    const ctx = document.getElementById('entropyChart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '系统熵值 (Entropy)',
                data: [],
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    grid: { color: '#334155' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { display: false }
                }
            }
        }
    });
}

async function toggleSimu() {
    if (running) {
        await stopSimu();
    } else {
        await startSimu();
    }
}

async function startSimu(){
    try {
        const response = await fetch('/api/start');
        if (!response.ok) throw new Error('Failed to start simulation');
        
        running = true;
        document.getElementById("ctrlBtn").innerText = "停止仿真";
        document.getElementById("statusVal").innerText = "运行中";
        document.getElementById("statusVal").style.color = "#22c55e";
        document.getElementById("result").innerText = "正在实时同步后端仿真引擎数据...";
        
        chart.data.labels = [];
        chart.data.datasets[0].data = [];
        
        // 开始轮询状态
        pollStatus();
    } catch (err) {
        console.error(err);
        alert("启动失败: " + err.message);
    }
}

async function pollStatus() {
    if (!running) return;

    try {
        const response = await fetch('/api/status?t=' + Date.now());
        const data = await response.json();
        console.log("Poll Data:", data);

        if (data.step > 0) {
            // 更新图表
            chart.data.labels.push(data.step);
            chart.data.datasets[0].data.push(data.entropy);
            if (chart.data.labels.length > 50) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }
            chart.update('none');

            // 更新报告（如果稳定了）
            if (data.is_stable) {
                stopSimu(true, data); // 传递 data 以便获取报告
                return;
            }
        }

        if (running) {
            setTimeout(pollStatus, 200); // 200ms 轮询一次
        }
    } catch (err) {
        console.error("轮询失败:", err);
    }
}

async function stopSimu(isAuto = false, data = null) {
    running = false;
    try {
        await fetch('/api/stop');
    } catch (err) {
        console.error("停止请求失败:", err);
    }

    document.getElementById("ctrlBtn").innerText = "启动仿真";
    document.getElementById("statusVal").innerText = isAuto ? "已完成" : "已停止";
    document.getElementById("statusVal").style.color = isAuto ? "#38bdf8" : "#f43f5e";
    
    if (isAuto && data && data.report) {
        const report = data.report;
        document.getElementById("result").innerText = 
        "✅ 仿真引擎报告：系统已达到动态平衡\n\n" +
        "【核心洞察】\n" +
        "1. 必做配置: " + report.must_have.join("、") + "\n" +
        "2. 风险预警: " + report.risk.join(" | ") + "\n" +
        "3. 推荐KOL类型: " + report.kol_best.join("、") + "\n" +
        "4. 竞品状态: " + (report.competitor_status === 'attack' ? '正在发动攻击' : '正常竞争');
    } else if (isAuto) {
        document.getElementById("result").innerText = "✅ 仿真完成，但未获取到详细报告。";
    }
}

window.onload = initChart;
