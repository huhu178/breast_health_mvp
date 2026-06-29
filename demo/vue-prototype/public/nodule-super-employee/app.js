const views = {
  command: "增长指挥",
  ip: "IP打造",
  creative: "创意选题",
  production: "内容生产",
  avatar: "数字人视频",
  matrix: "矩阵发布",
  prospecting: "平台拓客",
  leads: "线索池",
  deal: "私域成交",
  service: "健康管理",
  assets: "素材资产",
  analytics: "数据罗盘"
};

const pipeline = [
  ["IP定位", "结节健康管理师、报告解读陪跑官、食材分析师", "已配置"],
  ["爆款选题", "对标拆解 + 评论区问题 + 服务案例反哺", "12条"],
  ["AI生产", "标题、脚本、图文、海报、私信话术", "36条"],
  ["数字人", "口播视频、字幕、封面、作品库", "12条"],
  ["矩阵发布", "抖音、快手、小红书、视频号、朋友圈", "18条"],
  ["平台拓客", "对标拓客、关键词拓客、视频评论采集", "128线索"],
  ["私域成交", "问卷、报告、体验营、长期服务", "23高意向"],
  ["服务反哺", "周总结、食材问题、报告问题转内容", "9素材"]
];

const noduleBoard = [
  ["乳腺结节", "3,256", "+32", 356, 812, 188, 38, 22, 19, "81.2%"],
  ["甲状腺结节", "3,128", "+28", 312, 790, 176, 29, 18, 15, "79.4%"],
  ["肺部结节", "4,012", "+41", 428, "1,102", 226, 42, 24, 28, "77.8%"],
  ["肺部合并乳腺结节", "812", "+9", 96, 208, 46, 10, 6, 8, "74.4%"],
  ["随访合并甲状腺结节", "702", "+7", 84, 176, 39, 8, 4, 6, "76.1%"],
  ["甲状腺合并乳腺结节", "456", "+5", 52, 120, 28, 6, 3, 4, "77.2%"],
  ["三合并结节", "120", "+2", 20, 36, 9, 3, 2, 2, "72.0%"]
];

const todayTodos = [
  ["待处理报告", "146", "影像报告待处理，请尽快处理", "blue"],
  ["待问卷建档", "82", "客户已加微，需完成基础问卷", "green"],
  ["待推送体验营", "95", "已完成问卷，需及时推送", "purple"],
  ["异常预警", "102", "存在异常结节咨询，需优先处理", "orange"]
];

const notices = [
  ["高风险患者张女士随访已逾期7天，请尽快处理！", "08:45"],
  ["有18份报告超过24小时未处理", "08:30"],
  ["小红书食材清单笔记评论区出现32条咨询", "07:50"]
];

const typeLegend = [
  ["乳腺结节", "26.1%", "blue"],
  ["甲状腺结节", "25.1%", "cyan"],
  ["肺部结节", "32.1%", "green"],
  ["肺部合并乳腺结节", "6.5%", "orange"],
  ["随访合并甲状腺结节", "5.6%", "purple"],
  ["甲状腺合并乳腺结节", "3.7%", "pink"],
  ["三合并结节", "1.0%", "gray"]
];

const riskBars = [
  ["高意向", "1,348", "18%", "red"],
  ["中意向", "3,244", "44%", "orange"],
  ["低意向", "7,894", "88%", "green"]
];

const statusBars = [
  ["待处理报告", "146", "16%", "purple"],
  ["待问卷建档", "82", "10%", "cyan"],
  ["待推送患者", "95", "12%", "green"],
  ["随访中", "7,361", "78%", "blue"],
  ["异常待处理", "102", "14%", "red"],
  ["随访已完成", "9,248", "92%", "green"]
];

const platformTasks = [
  ["抖音", "肺结节复查前先整理这4个字段", "18:30发布"],
  ["快手", "结节客户晚睡焦虑，先别急着忌口", "20:00发布"],
  ["小红书", "甲状腺结节饮食避坑清单", "待审核"],
  ["视频号", "7天结节打卡体验营说明", "待生成"],
  ["朋友圈", "客户报告整理案例复盘", "待发布"]
];

const urgentLeads = [
  ["张女士", "抖音私信：已发乳腺报告", "S级"],
  ["周先生", "快手评论：肺结节复查焦虑", "A级"],
  ["何女士", "小红书私信：甲状腺能否吃海带", "A级"],
  ["马女士", "视频号直播：三结节想管理", "S级"]
];

const feedbackAssets = [
  ["客户问题", "豆浆、海带、牛奶到底怎么判断"],
  ["报告问题", "BI-RADS 3 类客户最焦虑"],
  ["服务案例", "7天打卡后睡眠记录改善"],
  ["复查提醒", "客户忘记复查日期，需提醒工具"]
];

const ipRoles = [
  ["结节健康管理师", "综合科普、案例、体验营说明", "视频号 / 朋友圈 / 小红书"],
  ["报告解读陪跑官", "报告字段、复查提醒、焦虑安抚", "抖音 / 快手"],
  ["食材分析师", "食材问答、红黑榜、清单资料", "小红书 / 社群"],
  ["7天打卡陪跑官", "饮食、睡眠、运动、情绪记录", "朋友圈 / 私域"],
  ["复查提醒规划师", "复查节点、报告变化记录", "抖音 / 视频号"],
  ["三结节管理顾问", "乳腺、甲状腺、肺结节综合管理", "私域成交"]
];

const creativeRoles = [
  ["对标专员", "拆解抖音、快手、小红书、视频号同行内容", "同行监控"],
  ["选题专家", "从评论区和问卷里提炼客户最想问的问题", "选题广场"],
  ["编导老师", "把专业内容变成3秒钩子、分镜和口播", "脚本拆解"],
  ["提示词工程师", "沉淀结节项目专用Prompt和合规边界", "Prompt库"]
];

let topicOffset = 0;
const topicGroups = [
  [
    ["报告解读", "乳腺结节 BI-RADS 3 类到底要不要慌", "抖音 / 小红书"],
    ["复查提醒", "肺结节复查前，一定要整理这4个字段", "抖音 / 视频号"],
    ["食材问答", "甲状腺结节能不能吃海带，关键不在海带本身", "小红书"]
  ],
  [
    ["焦虑安抚", "看到结节两个字就睡不着，先做这一步", "快手 / 视频号"],
    ["服务转化", "为什么结节管理要先填问卷再给建议", "朋友圈 / 社群"],
    ["案例复盘", "一个三结节客户的7天打卡路径", "视频号 / 朋友圈"]
  ]
];

const benchmarks = [
  ["抖音对标", "体检科普账号评论区：报告看不懂、复查害怕", "生成3条口播"],
  ["快手对标", "生活化健康账号：客户更吃案例和陪跑感", "生成2条案例"],
  ["小红书对标", "女性健康笔记：食材避坑和清单收藏率高", "生成5篇笔记"],
  ["视频号对标", "直播答疑切片：专业信任更利于加微", "生成直播话术"]
];

const templates = [
  ["抖音", "高钩子短视频", "3秒钩子 + 专业解释 + 评论关键词"],
  ["快手", "生活化口播", "真实问题 + 陪跑口吻 + 私信引导"],
  ["小红书", "清单图文", "标题关键词 + 避坑清单 + 领取资料"],
  ["视频号", "专业科普", "稳重讲解 + 朋友圈联动 + 问卷入口"],
  ["朋友圈", "信任养熟", "客户问题 + 服务过程 + 低压力邀约"],
  ["社群", "答疑转化", "每日科普 + 群内问答 + 体验营报名"]
];

let videos = [
  ["数字人口播", "甲状腺结节能不能吃海带", "待审核"],
  ["报告解读", "乳腺BI-RADS 3类怎么看", "已生成"],
  ["复查提醒", "肺结节复查前准备清单", "待发布"],
  ["体验营说明", "7天打卡流程介绍", "生成中"]
];

let schedules = [
  ["抖音账号A", "肺结节复查提醒", "明日 18:30"],
  ["快手账号B", "结节客户食材误区", "明日 20:00"],
  ["小红书账号C", "甲状腺结节饮食清单", "明日 12:10"],
  ["视频号账号D", "体验营说明视频", "明日 19:40"]
];

const accounts = [
  ["抖音", "结节报告陪跑官", "在线", "今日2条"],
  ["快手", "结节管理师小枫", "在线", "今日1条"],
  ["小红书", "结节食材分析师", "待登录", "今日3篇"],
  ["视频号", "结节健康管理", "在线", "今日1条"],
  ["朋友圈", "管理师企微1号", "在线", "今日5条"]
];

const prospectPlatforms = [
  ["抖音", "对标拓客 / 视频拓客 / 评论采集", "报告解读、复查焦虑"],
  ["快手", "评论采集 / 直播预热 / 私信预设", "生活化案例、陪跑服务"],
  ["小红书", "关键词拓客 / 笔记评论 / 私信承接", "食材避坑、女性结节"],
  ["视频号", "直播线索 / 评论线索 / 朋友圈联动", "专业信任、私域转化"],
  ["大众点评", "本地健康服务线索", "门店合作可用"],
  ["美团", "本地咨询和评价线索", "线下服务可用"]
];

const prospectTasks = [
  ["对标拓客", "采集3个乳腺健康账号近7天热门评论", "待人工确认"],
  ["关键词拓客", "搜索甲状腺结节、海带、豆浆、复查", "已生成线索"],
  ["视频拓客", "肺结节爆款视频评论区意图识别", "64条评论"],
  ["地图获客", "体检中心/中医馆/健康管理合作线索", "二期任务"]
];

let leadRows = [
  ["张女士", "抖音私信", "乳腺报告看不懂，已发图", "已加微", 92, "发问卷"],
  ["何女士", "小红书评论", "甲状腺结节能不能吃海带", "待私信", 76, "发食材问卷"],
  ["周先生", "快手评论", "肺结节复查间隔焦虑", "待加微", 71, "安抚+复查表"],
  ["马女士", "视频号直播", "三结节，想系统管理", "已问卷", 95, "邀约体验营"],
  ["刘女士", "朋友圈转介绍", "乳腺结节睡眠差", "已建档", 88, "进入打卡"]
];

const scoreRules = [
  ["私信咨询", "+20"],
  ["愿意加微", "+30"],
  ["完成问卷", "+40"],
  ["发送报告", "+50"],
  ["询问价格", "+60"],
  ["老客转介绍", "+70"]
];

const conversations = [
  ["张女士", "抖音私信 · 已发报告", "我这个乳腺结节报告严重吗？", "先安抚焦虑，再引导她填基础问卷，整理报告字段后进入7天体验。"],
  ["何女士", "小红书私信 · 食材咨询", "甲状腺结节到底能不能吃海带？", "不要直接说能或不能，先问甲功、频次和食用量，引导做食材判断问卷。"],
  ["马女士", "视频号直播 · 三结节", "我三个地方都有结节，能不能系统管？", "强调多结节更需要记录和复查节点，建议先建档再做体验打卡。"]
];

const replies = {
  comfort: "先别太焦虑，单看“结节”两个字不能判断严重程度。我们可以先把报告字段、复查时间和生活习惯整理清楚，再看适合怎么做健康管理。",
  questionnaire: "我先发您一个基础问卷，里面会了解结节类型、报告情况、饮食、睡眠、运动和情绪，填完后我帮您整理初步管理重点。",
  report: "您可以把最近一次报告原图发来，我帮您整理健康管理关注点。诊断、用药和治疗方案仍以医生意见为准。",
  camp: "可以先从7天体验打卡开始，每天记录饮食、睡眠、运动和不适反馈，第7天做一次复盘，再判断是否需要长期管理。",
  doctor: "这部分涉及医学诊断和治疗决策，建议以医生面诊意见为准。我们这边主要帮您做生活方式记录、复查提醒和健康管理陪跑。"
};

const patients = [
  ["刘秀娟", "乳腺结节", "第2周打卡", "李慧玲", "复盘饮食和睡眠"],
  ["吴强", "甲状腺+肺结节", "方案执行", "王老师", "提醒复查报告"],
  ["盛玲玲", "乳腺结节", "第4月随访", "李慧玲", "生成月总结"],
  ["王玉杰", "三结节", "问卷待补", "陈老师", "补充舌苔图片"]
];

const servicePipeline = [
  ["问卷建档", "结节类型、报告字段、复查节点"],
  ["报告记录", "大小、分级、医生建议、日期"],
  ["7天打卡", "饮食、睡眠、运动、情绪、不适"],
  ["食材分析", "结合类型、频次和个体反应"],
  ["体验总结", "第7天生成复盘和长期建议"],
  ["案例反哺", "脱敏转成内容、问答和海报"]
];

const assets = [
  ["文案", "甲状腺结节食材问答脚本", "小红书 / 抖音"],
  ["图片", "食材红黑榜海报", "朋友圈 / 社群"],
  ["音频", "数字人温和女声", "口播"],
  ["视频", "肺结节复查提醒口播", "抖音 / 快手"],
  ["案例", "7天打卡体验总结", "朋友圈"],
  ["问答", "BI-RADS 3类怎么理解", "客服话术"]
];

const analyticsBars = [
  ["抖音", "46%", "曝光高，报告解读和复查提醒贡献最大"],
  ["快手", "31%", "评论互动强，案例和陪跑感内容有效"],
  ["小红书", "42%", "食材避坑、清单类笔记转问卷更高"],
  ["视频号", "28%", "私域信任强，适合直播和体验营转化"],
  ["朋友圈", "35%", "养熟和成交稳定，适合案例复盘"]
];

const contentRank = [
  ["食材问答", "甲状腺结节能不能吃海带", "带来31条线索"],
  ["报告解读", "BI-RADS 3类到底要不要慌", "带来18份报告"],
  ["复查提醒", "肺结节复查前准备4类资料", "带来12个加微"],
  ["体验营", "7天结节打卡怎么做", "带来9个报名"]
];

function $(selector) {
  return document.querySelector(selector);
}

function renderList(selector, rows, hot = false) {
  $(selector).innerHTML = rows.map(([title, desc, badge]) => `
    <article class="list-item">
      <div><strong>${title}</strong><small>${desc}</small></div>
      <span class="badge ${hot || badge === "S级" ? "hot" : ""}">${badge}</span>
    </article>
  `).join("");
}

function switchView(id) {
  document.querySelectorAll(".view").forEach((view) => view.classList.toggle("active", view.id === id));
  document.querySelectorAll(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.view === id));
  $("#page-title").textContent = views[id];
}

function renderPipeline(selector, rows) {
  $(selector).innerHTML = rows.map(([title, desc, badge]) => `
    <article class="pipeline-step">
      <strong>${title}</strong>
      <span>${desc}</span>
      <b>${badge}</b>
    </article>
  `).join("");
}

function renderCommand() {
  $("#nodule-board").innerHTML = noduleBoard.map((row) => {
    const [type, total, today, high, questionnaire, report, pending, camp, deal, rate] = row;
    return `
      <tr>
        <td><span class="type-name">${type}</span></td>
        <td>${total}</td>
        <td class="positive">${today}</td>
        <td class="danger-text">${high}</td>
        <td class="warn-text">${questionnaire}</td>
        <td class="green-text">${report}</td>
        <td>${pending}</td>
        <td>${camp}</td>
        <td>${deal}</td>
        <td><span class="progress"><i style="--value:${rate}"></i></span>${rate}</td>
        <td><button class="mini-btn" data-jump="leads">进入队列</button></td>
      </tr>
    `;
  }).join("");

  $("#today-todos").innerHTML = todayTodos.map(([name, count, desc, tone]) => `
    <article class="todo-item ${tone}">
      <b>${name}</b>
      <strong>${count}</strong>
      <span>${desc}</span>
    </article>
  `).join("");

  $("#notice-list").innerHTML = notices.map(([text, time]) => `
    <article class="notice-item"><span>${text}</span><small>${time}</small></article>
  `).join("");

  $("#type-legend").innerHTML = typeLegend.map(([name, value, color]) => `
    <article><i class="${color}"></i><span>${name}</span><b>${value}</b></article>
  `).join("");

  $("#risk-bars").innerHTML = riskBars.map(([name, value, width, tone]) => `
    <article class="hbar-row"><span>${name}</span><div class="hbar"><i class="${tone}" style="--value:${width}"></i></div><b>${value}</b></article>
  `).join("");

  $("#status-bars").innerHTML = statusBars.map(([name, value, width, tone]) => `
    <article class="hbar-row"><span>${name}</span><div class="hbar"><i class="${tone}" style="--value:${width}"></i></div><b>${value}</b></article>
  `).join("");
}

function renderIp() {
  $("#ip-grid").innerHTML = ipRoles.map(([name, desc, channels]) => `
    <article class="ip-card">
      <strong>${name}</strong>
      <span>${desc}</span>
      <small>${channels}</small>
    </article>
  `).join("");
}

function renderCreative() {
  $("#creative-roles").innerHTML = creativeRoles.map(([name, desc, tag]) => `
    <article class="role-card"><strong>${name}</strong><span>${desc}</span><b>${tag}</b></article>
  `).join("");
  renderList("#benchmark-list", benchmarks);
  const group = topicGroups[topicOffset % topicGroups.length];
  $("#topic-board").innerHTML = group.map(([type, title, platform]) => `
    <article class="topic-card"><span>${type}</span><strong>${title}</strong><small>${platform}</small><button class="ghost full" data-jump="production">生成内容</button></article>
  `).join("");
}

function generateContent() {
  const platform = $("#platform-select").value;
  const persona = $("#persona-select").value;
  const nodule = $("#nodule-select").value;
  const goal = $("#goal-select").value;
  const topic = $("#content-topic").value.trim() || "结节客户如何做健康管理";
  const platformTone = {
    抖音: "开头必须更抓人，用3秒钩子切入，评论区用关键词承接。",
    快手: "表达更生活化，像管理师和客户面对面聊天。",
    小红书: "结构要清单化，标题带关键词，适合收藏和私信。",
    视频号: "语气更稳重，适合专业信任和私域承接。",
    朋友圈: "强调真实服务过程，用低压力方式邀约问卷。",
    社群: "适合每日科普和群内答疑，引导体验营报名。"
  }[platform];

  $("#content-output").innerHTML = `
    <article class="output-card">
      <b>标题</b>
      <strong>${topic}，先别急着下结论，先看这3个管理重点</strong>
      <span>${platform} · ${persona} · ${goal}</span>
    </article>
    <article class="output-card">
      <b>口播/正文</b>
      <p>很多${nodule}客户最焦虑的不是一个食材或一个指标，而是不知道自己应该记录什么。先把报告字段、复查日期、饮食频次、睡眠情绪整理出来，再决定下一步怎么做健康管理。</p>
    </article>
    <article class="output-card">
      <b>平台适配</b>
      <p>${platformTone}</p>
    </article>
    <article class="output-card">
      <b>私信承接</b>
      <p>如果你也想整理自己的${nodule}管理重点，可以先做一份基础问卷，我帮你把饮食、复查和打卡方向梳理出来。</p>
    </article>
    <article class="output-card">
      <b>合规提醒</b>
      <p>不承诺治疗效果，不替代医生诊断。涉及诊断、用药、手术和复查间隔，以医生建议为准。</p>
    </article>
  `;
}

function renderProduction() {
  $("#template-grid").innerHTML = templates.map(([platform, type, desc]) => `
    <article class="template-card"><strong>${platform}</strong><span>${type}</span><small>${desc}</small></article>
  `).join("");
  generateContent();
}

function renderAvatar() {
  $("#video-grid").innerHTML = videos.map(([type, title, status]) => `
    <article class="video-card">
      <div class="video-thumb">${type.slice(0, 2)}</div>
      <strong>${title}</strong>
      <span>${type}</span>
      <b>${status}</b>
    </article>
  `).join("");
}

function renderMatrix() {
  renderList("#schedule-list", schedules);
  $("#account-grid").innerHTML = accounts.map(([platform, name, status, task]) => `
    <article class="account-card"><strong>${platform}</strong><span>${name}</span><small>${status} · ${task}</small></article>
  `).join("");
  $("#video-assets").innerHTML = videos.map(([type, title, status]) => `<article><b>${type}</b><span>${title}</span><small>${status}</small></article>`).join("");
}

function renderProspecting() {
  $("#prospect-platforms").innerHTML = prospectPlatforms.map(([platform, tools, desc]) => `
    <article class="platform-card"><strong>${platform}</strong><span>${tools}</span><small>${desc}</small></article>
  `).join("");
  renderList("#prospect-tasks", prospectTasks);
}

function renderLeads() {
  $("#lead-table").innerHTML = leadRows.map((row) => `
    <tr>${row.map((cell, index) => `<td>${index === 4 ? `<span class="score">${cell}</span>` : cell}</td>`).join("")}</tr>
  `).join("");
  $("#score-list").innerHTML = scoreRules.map(([rule, score]) => `<article class="score-row"><span>${rule}</span><b>${score}</b></article>`).join("");
}

function renderDeal(index = 0) {
  $("#conversation-list").innerHTML = conversations.map((row, i) => `
    <button class="conversation ${i === index ? "active" : ""}" data-chat="${i}">
      <strong>${row[0]}</strong>
      <small>${row[1]}</small>
      <small>${row[2]}</small>
    </button>
  `).join("");
  const current = conversations[index];
  $("#chat-name").textContent = current[0];
  $("#chat-stage").textContent = current[1];
  $("#messages").innerHTML = `<div class="msg customer">${current[2]}</div><div class="msg staff">${replies.comfort}</div>`;
  $("#sales-advice").textContent = current[3];
}

function renderService() {
  $("#patient-table").innerHTML = patients.map((row) => `<tr>${row.map((cell) => `<td>${cell}</td>`).join("")}</tr>`).join("");
  renderPipeline("#service-pipeline", servicePipeline.map(([a, b]) => [a, b, "SOP"]));
  analyzeFood();
}

function analyzeFood() {
  const food = $("#food-input").value.trim() || "豆浆";
  $("#food-output").innerHTML = `<strong>${food}可发话术：</strong><br>不要只按“能不能吃”来判断，建议结合结节类型、报告情况、食用频次和个人反应记录。可以先少量低频，并在打卡里记录当天睡眠、胃肠反应和不适情况；涉及疾病治疗和用药仍以医生建议为准。`;
}

function renderAssets() {
  $("#asset-grid").innerHTML = assets.map(([type, title, scene]) => `
    <article class="asset-card"><b>${type}</b><strong>${title}</strong><span>${scene}</span><button class="ghost full">查看素材</button></article>
  `).join("");
}

function renderAnalytics() {
  $("#analytics-bars").innerHTML = analyticsBars.map(([name, value, desc]) => `
    <article class="bar-item">
      <div><strong>${name}</strong><small>${desc}</small><div class="bar"><i style="--value:${value}"></i></div></div>
      <span class="badge">${value}</span>
    </article>
  `).join("");
  renderList("#content-rank", contentRank);
}

document.querySelectorAll(".nav-item").forEach((button) => button.addEventListener("click", () => switchView(button.dataset.view)));
document.addEventListener("click", (event) => {
  const jump = event.target.closest("[data-jump]");
  if (jump) switchView(jump.dataset.jump);
});

$("#next-topic").addEventListener("click", () => {
  topicOffset += 1;
  renderCreative();
});

$("#ip-random").addEventListener("click", () => {
  const first = ipRoles.shift();
  ipRoles.push(first);
  renderIp();
});

$("#generate-content").addEventListener("click", generateContent);
$("#send-avatar").addEventListener("click", () => switchView("avatar"));
$("#make-video").addEventListener("click", () => {
  videos.unshift(["数字人口播", $("#content-topic")?.value || "结节健康管理口播", "刚生成"]);
  renderAvatar();
});
$("#add-schedule").addEventListener("click", () => {
  schedules.unshift(["抖音账号A", "新生成数字人口播", "明日 21:10"]);
  renderMatrix();
});
$("#run-prospect").addEventListener("click", () => {
  leadRows.unshift(["新线索", "抖音评论", "评论区咨询结节饮食", "待私信", 68, "人工确认"]);
  renderLeads();
  switchView("leads");
});
$("#fill-prospect").addEventListener("click", () => {
  prospectTasks.unshift(["对标拓客", "采集抖音/小红书结节科普账号：20条视频、近7天评论、人工确认私信", "新建任务"]);
  renderProspecting();
});
$("#score-leads").addEventListener("click", () => {
  leadRows = leadRows.map((row) => {
    const next = [...row];
    next[4] = Math.min(99, Number(next[4]) + 3);
    return next;
  });
  renderLeads();
});

$("#conversation-list").addEventListener("click", (event) => {
  const target = event.target.closest("[data-chat]");
  if (target) renderDeal(Number(target.dataset.chat));
});

document.querySelector(".quick-replies").addEventListener("click", (event) => {
  const target = event.target.closest("[data-reply]");
  if (target) $("#reply-box").value = replies[target.dataset.reply];
});

$("#send-reply").addEventListener("click", () => {
  const text = $("#reply-box").value.trim();
  if (!text) return;
  const msg = document.createElement("div");
  msg.className = "msg staff";
  msg.textContent = text;
  $("#messages").appendChild(msg);
  $("#reply-box").value = "";
});

$("#food-btn").addEventListener("click", analyzeFood);

renderCommand();
renderIp();
renderCreative();
renderProduction();
renderAvatar();
renderMatrix();
renderProspecting();
renderLeads();
renderDeal();
renderService();
renderAssets();
renderAnalytics();
