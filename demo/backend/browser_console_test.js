/**
 * 浏览器控制台快速测试脚本
 *
 * 使用方法：
 * 1. 在浏览器中登录系统
 * 2. 打开开发者工具（F12）
 * 3. 切换到 Console 标签
 * 4. 复制粘贴下面的代码并回车
 */

(async function testReportWorkflow() {
    const REPORT_ID = 74;
    const BASE_URL = '/api/b/reports';

    console.log('\n' + '='.repeat(60));
    console.log('开始测试报告审核工作流');
    console.log('='.repeat(60));

    try {
        // 步骤1: 查看草稿报告
        console.log('\n[步骤1] 查看草稿报告');
        console.log(`GET ${BASE_URL}/${REPORT_ID}`);

        const viewResponse = await fetch(`${BASE_URL}/${REPORT_ID}`);
        const viewData = await viewResponse.json();

        if (viewData.success) {
            console.log('✅ 成功获取报告');
            console.log('   报告ID:', viewData.data.id);
            console.log('   状态:', viewData.data.status);
            console.log('   影像学结论:', viewData.data.imaging_conclusion?.substring(0, 100) + '...');
            console.log('   疾病史结论:', viewData.data.medical_conclusion?.substring(0, 100) + '...');
            console.log('   风险等级:', viewData.data.risk_level);
            console.log('   风险评分:', viewData.data.risk_score);
        } else {
            console.error('❌ 失败:', viewData.message);
            return;
        }

        // 步骤2: 编辑评估内容
        console.log('\n[步骤2] 编辑评估内容');
        console.log(`PUT ${BASE_URL}/${REPORT_ID}`);

        const editResponse = await fetch(`${BASE_URL}/${REPORT_ID}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                imaging_conclusion: '【管理师审核修改】影像学评估：经过专业审核，确认AI评估结果准确，患者影像学表现符合良性病变特征...',
                review_notes: '已完成初步审核，内容准确，建议发布'
            })
        });
        const editData = await editResponse.json();

        if (editData.success) {
            console.log('✅ 成功更新报告');
            console.log('   更新后的影像学结论:', editData.data.imaging_conclusion?.substring(0, 100) + '...');
            console.log('   审核备注:', editData.data.review_notes);
        } else {
            console.error('❌ 失败:', editData.message);
            return;
        }

        // 步骤3: 审核发布
        console.log('\n[步骤3] 审核通过并发布报告');
        console.log(`POST ${BASE_URL}/${REPORT_ID}/publish`);

        const publishResponse = await fetch(`${BASE_URL}/${REPORT_ID}/publish`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                review_notes: '最终审核通过，内容准确完整，准予发布'
            })
        });
        const publishData = await publishResponse.json();

        if (publishData.success) {
            console.log('✅ 成功发布报告');
            console.log('   状态:', publishData.data.status);
            console.log('   审核人ID:', publishData.data.reviewed_by);
            console.log('   审核时间:', publishData.data.reviewed_at);
            console.log('   审核备注:', publishData.data.review_notes);
        } else {
            console.error('❌ 失败:', publishData.message);
            return;
        }

        // 步骤4: 导出报告HTML
        console.log('\n[步骤4] 导出完整的健康报告HTML');
        console.log(`GET ${BASE_URL}/${REPORT_ID}/comprehensive`);

        const exportResponse = await fetch(`${BASE_URL}/${REPORT_ID}/comprehensive`);

        if (exportResponse.ok) {
            const htmlContent = await exportResponse.text();
            console.log('✅ 成功生成报告HTML');
            console.log('   HTML长度:', htmlContent.length, '字符');

            // 在新窗口打开HTML预览
            const previewWindow = window.open('', '_blank');
            previewWindow.document.write(htmlContent);
            previewWindow.document.close();
            console.log('   ✅ 已在新窗口打开HTML预览');
        } else {
            const errorData = await exportResponse.json();
            console.error('❌ 失败:', errorData.message);
            return;
        }

        console.log('\n' + '='.repeat(60));
        console.log('✅✅✅ 所有测试通过！工作流运行正常！');
        console.log('='.repeat(60));

    } catch (error) {
        console.error('❌ 测试过程中发生异常:', error);
    }
})();
