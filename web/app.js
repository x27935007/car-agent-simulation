let chart;
let running = false;
let user = localStorage.getItem('sim_user');
let pwd = localStorage.getItem('sim_pwd');

// 鉴权跳转
if (!user || !pwd) {
    location.href = "/";
}

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

// 加载车型和初始状态
async function initPage() {
    document.getElementById('userDisplay').innerText = user;
    
    // 加载车型
    try {
        const r = await fetch("/api/car_models");
        const d = await r.json();
        const select = document.getElementById('carModel');
        d.models.forEach(m => {
            const opt = document.createElement('option');
            opt.value = m.id;
            opt.innerText = m.name;
            select.appendChild(opt);
        });
    } catch (e) { console.error("加载车型失败"); }

    // 获取余额
    updateBalance();
    initChart();
}

async function updateBalance() {
    try {
        const r = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user, pwd })
        });
        const d = await r.json();
        if (d.ok) document.getElementById('balanceDisplay').innerText = d.balance;
    } catch (e) {}
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
        const response = await fetch('/api/start', {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user, pwd, model_id: document.getElementById('carModel').value })
        });
        const data = await response.json();
        
        if (!data.ok) {
            alert(data.msg || "启动失败");
            return;
        }
        
        running = true;
        document.getElementById("balanceDisplay").innerText = data.balance;
        document.getElementById("ctrlBtn").innerText = "停止仿真";
        document.getElementById("statusVal").innerText = "运行中";
        document.getElementById("statusVal").style.color = "#22c55e";
        document.getElementById("result").innerText = "正在同步 SaaS 云端引擎仿真数据...";
        
        chart.data.labels = [];
        chart.data.datasets[0].data = [];
        pollStatus();
    } catch (err) {
        alert("启动请求失败");
    }
}

async function pollStatus() {
    if (!running) return;

    try {
        const response = await fetch('/api/status?t=' + Date.now());
        const data = await response.json();

        if (data.step > 0) {
            chart.data.labels.push(data.step);
            chart.data.datasets[0].data.push(data.entropy);
            if (chart.data.labels.length > 50) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }
            chart.update('none');

            if (data.is_stable) {
                stopSimu(true, data);
                return;
            }
        }

        if (running) setTimeout(pollStatus, 200);
    } catch (err) { console.error("轮询失败"); }
}

async function stopSimu(isAuto = false, data = null) {
    running = false;
    try {
        await fetch('/api/stop', { method: "POST" });
    } catch (err) {}

    document.getElementById("ctrlBtn").innerText = "启动仿真 (扣除1点)";
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
    }
}

window.onload = initPage;
