<template>
  <div class="record-page">
    <div class="record-card">
      <div class="record-card-head">
        <div class="record-page-title">{{ scenario.recordLabel }}</div>
        <div class="record-page-sub">{{ recordSubtitle }}</div>
      </div>
      <div class="record-layout">
      <div class="record-form">

        <!-- 1. 基础信息 -->
        <section class="form-sec">
          <div class="sec-h"><span class="no">一</span>{{ scenario.personLabel }}基础信息</div>
          <div class="grid-12">
            <!-- 第1行：姓名、性别、出生日期/年龄、手机号 -->
            <div class="field col-3 required">
              <div class="label">姓名</div>
              <input v-model="form.name" placeholder="请输入姓名">
            </div>
            <div class="field col-2 required">
              <div class="label">性别</div>
              <select v-model="form.gender">
                <option>男</option><option>女</option>
              </select>
            </div>
            <div class="field col-3 required">
              <div class="label">出生日期</div>
              <input v-model="form.birthDate" type="date">
            </div>
            <div class="field col-1">
              <div class="label">年龄</div>
              <input v-model="form.age" type="number" min="0" placeholder="自动" readonly>
            </div>
            <div class="field col-3 required phone">
              <div class="label">手机号</div>
              <input v-model="form.phone" placeholder="请输入手机号">
            </div>

            <!-- 第1.5行：身高、体重、糖尿病史 -->
            <div class="field col-2">
              <div class="label">身高（cm）</div>
              <input v-model="form.height" type="number" min="80" max="250" placeholder="例如：165">
            </div>
            <div class="field col-2">
              <div class="label">体重（kg）</div>
              <input v-model="form.weight" type="number" min="20" max="300" placeholder="例如：60">
            </div>
            <div class="field col-2">
              <div class="label">糖尿病史</div>
              <select v-model="form.diabetesHistory">
                <option>无</option>
                <option>有</option>
              </select>
            </div>

            <!-- 第2行：身份证号、联系地址、紧急联系人关系 -->
            <div class="field col-4 idno">
              <div class="label">身份证号</div>
              <input v-model="form.idNo" placeholder="请输入身份证号">
            </div>
            <div class="field col-5 addr">
              <div class="label">联系地址</div>
              <input v-model="form.addr" placeholder="省/市/区/详细地址">
            </div>
            <div class="field col-3">
              <div class="label">紧急联系人关系</div>
              <select v-model="form.emergency">
                <option>配偶</option><option>子女</option><option>父母</option><option>其他</option>
              </select>
            </div>

            <!-- 第3行：紧急联系人姓名、紧急联系人电话、备注 -->
            <div class="field col-3">
              <div class="label">紧急联系人姓名</div>
              <input v-model="form.emergencyName" placeholder="请输入姓名">
            </div>
            <div class="field col-3 phone">
              <div class="label">紧急联系人电话</div>
              <input v-model="form.emergencyPhone" placeholder="请输入电话">
            </div>
            <div class="field col-6 note">
              <div class="label">备注</div>
              <input v-model="form.note" placeholder="简短备注（不超过一行）">
            </div>
          </div>
        </section>

        <!-- 2. 来源信息 -->
        <section class="form-sec">
          <div class="sec-h"><span class="no">二</span>{{ scenario.personLabel }}来源</div>
          <div class="grid-12">
            <div class="field col-2 required">
              <div class="label">来源类型</div>
              <select v-model="form.source">
                <option v-for="src in scenario.sourceOptions" :key="src">{{ src }}</option>
              </select>
            </div>
            <div class="field col-2 required">
              <div class="label">所属科室</div>
              <select v-model="form.departmentId">
                <option value="">请选择科室</option>
                <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
              </select>
            </div>
            <div class="field col-2 required">
              <div class="label">主要负责医生</div>
              <select v-model="form.primaryDoctorId">
                <option value="">请选择医生</option>
                <option v-for="doctor in filteredDoctors" :key="doctor.id" :value="doctor.id">{{ doctor.real_name || doctor.username }}</option>
              </select>
            </div>
            <div class="field col-2 required">
              <div class="label">管理人员</div>
              <select v-model="form.managerId">
                <option value="">请选择管理人员</option>
                <option v-for="manager in managers" :key="manager.id" :value="manager.id">{{ manager.real_name || manager.username }}</option>
              </select>
            </div>
            <div class="field col-3 required">
              <div class="label">检查日期</div>
              <input v-model="form.examDate" type="date">
            </div>
          </div>
        </section>

        <!-- 3. 结节信息 -->
        <section class="form-sec">
          <div class="sec-h"><span class="no">三</span>结节信息</div>
          <div class="field-row">
            <div class="field-label"><span class="req">结节类型（可多选）</span></div>
            <div class="tag-row">
              <button
                v-for="t in organTags"
                :key="t"
                type="button"
                class="tag-btn"
                :class="{ active: selectedTag === t }"
                @click="toggleOrganType(t)"
              >
                {{ t }}
              </button>

              <span class="tag-divider" aria-hidden="true"></span>

              <button
                v-for="p in presetTags"
                :key="p.id"
                type="button"
                class="tag-btn preset"
                :class="{ active: selectedTag === p.id }"
                @click="applyPreset(p.id)"
              >
                {{ p.label }}
              </button>
            </div>
          </div>


          <div v-if="visibleNodules.includes('肺部结节')" class="nodule-mini">
            <div class="nodule-mini-title">肺部结节</div>
            <div class="form-grid cols3">
              <div class="form-field required">
                <div class="label">结节发现时间</div>
                <input v-model="form.lung_discovery_date" type="date">
              </div>
              <div class="form-field required">
                <div class="label">Lung-RADS分级</div>
                <select v-model="form.lung_rads_level">
                  <option>不清楚</option>
                  <option>1</option><option>2</option><option>3</option>
                  <option>4A</option><option>4B</option><option>4X</option>
                </select>
              </div>
              <div class="form-field">
                <div class="label">数量</div>
                <select v-model="form.lung_nodule_quantity">
                  <option value="">—</option>
                  <option>单发</option>
                  <option>多发</option>
                </select>
              </div>
              <div class="form-field">
                <div class="label">结节大小</div>
                <div class="input-unit">
                  <input v-model="form.lung_nodule_size" placeholder="例如：12.5">
                  <span class="unit">mm</span>
                </div>
              </div>
              <div v-if="String(form.lung_nodule_quantity||'').includes('多发')" class="form-field">
                <div class="label">多发结节个数</div>
                <input v-model="form.lung_nodule_count" type="number" min="1" placeholder="例如：3">
              </div>

              <div class="form-field full">
                <div class="label">肺部症状（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in ['无症状','咳嗽','咳痰','胸痛','气短','咯血','其他']"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.lung_symptoms||[]).includes(s) }"
                    @click="toggleArr(form.lung_symptoms, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.lung_symptoms||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.lung_symptoms_other" placeholder="请输入其他症状">
                </div>
              </div>

              <div class="form-field full">
                <div class="label">肺部基础疾病史（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in ['无','肺炎病史','肺结核病史','慢性阻塞性肺疾病','肺纤维化','肺癌病史','其他']"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.lung_cancer_history||[]).includes(s) }"
                    @click="toggleArr(form.lung_cancer_history, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.lung_cancer_history||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.lung_cancer_history_other" placeholder="请输入其他肺部疾病史">
                </div>
              </div>

              <div class="form-field full">
                <div class="label">肺部家族史（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in familyHistoryOptions"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.lung_family_history||[]).includes(s) }"
                    @click="toggleArr(form.lung_family_history, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.lung_family_history||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.lung_family_history_other" placeholder="请输入其他家族史">
                </div>
              </div>

              <div class="form-field full">
                <div class="label">肺部药物使用史（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in ['无','中成药治疗','激素调节药物','维生素辅助治疗','其他']"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.lung_medication_history||[]).includes(s) }"
                    @click="toggleArr(form.lung_medication_history, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.lung_medication_history||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.lung_medication_other" placeholder="请输入其他药物使用史">
                </div>
              </div>
            </div>
          </div>

          <div v-if="visibleNodules.includes('甲状腺结节')" class="nodule-mini">
            <div class="nodule-mini-title">甲状腺结节</div>
            <div class="form-grid cols3">
              <div class="form-field">
                <div class="label">结节发现时间</div>
                <input v-model="form.thyroid_discovery_date" type="date">
              </div>
              <div class="form-field required">
                <div class="label">TI-RADS分级</div>
                <select v-model="form.tirads_level">
                  <option>不清楚</option>
                  <option>1</option><option>2</option><option>3</option>
                  <option>4A</option><option>4B</option><option>4C</option>
                  <option>5</option><option>6</option>
                </select>
              </div>
              <div class="form-field">
                <div class="label">数量</div>
                <select v-model="form.thyroid_nodule_quantity">
                  <option value="">—</option>
                  <option>单发</option>
                  <option>多发</option>
                </select>
              </div>
              <div class="form-field">
                <div class="label">结节大小</div>
                <div class="input-unit">
                  <input v-model="form.thyroid_nodule_size" placeholder="例如：12.5">
                  <span class="unit">mm</span>
                </div>
              </div>
              <div v-if="String(form.thyroid_nodule_quantity||'').includes('多发')" class="form-field">
                <div class="label">多发结节个数</div>
                <input v-model="form.thyroid_nodule_count" type="number" min="1" placeholder="例如：3">
              </div>

              <div class="form-field full">
                <div class="label">结节症状（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in ['无症状','颈部肿块','压迫症状','疼痛症状','其他']"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.thyroid_symptoms||[]).includes(s) }"
                    @click="toggleArr(form.thyroid_symptoms, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.thyroid_symptoms||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.thyroid_symptoms_other" placeholder="请输入其他症状">
                </div>
              </div>

              <div class="form-field full">
                <div class="label">甲状腺基础疾病史（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in ['无','甲状腺功能亢进（甲亢）','甲状腺功能减退（甲减）','桥本甲状腺炎','亚急性甲状腺炎','甲状腺癌病史','其他']"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.hypothyroidism_history||[]).includes(s) }"
                    @click="toggleArr(form.hypothyroidism_history, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.hypothyroidism_history||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.hypothyroidism_history_other" placeholder="请输入其他甲状腺疾病史">
                </div>
              </div>

              <div class="form-field full">
                <div class="label">甲状腺家族史（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in familyHistoryOptions"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.thyroid_family_history||[]).includes(s) }"
                    @click="toggleArr(form.thyroid_family_history, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.thyroid_family_history||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.thyroid_family_history_other" placeholder="请输入其他家族史">
                </div>
              </div>

              <div class="form-field full">
                <div class="label">甲状腺药物使用史（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in ['无','甲状腺激素治疗','抗甲状腺药物','放射性碘治疗','中成药治疗','其他']"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.thyroid_medication_history||[]).includes(s) }"
                    @click="toggleArr(form.thyroid_medication_history, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.thyroid_medication_history||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.thyroid_medication_other" placeholder="请输入其他药物使用史">
                </div>
              </div>
            </div>
          </div>

          <div v-if="visibleNodules.includes('乳腺结节')" class="nodule-mini">
            <div class="nodule-mini-title">乳腺结节</div>
            <div class="form-grid cols3">
              <div class="form-field required">
                <div class="label">结节发现时间</div>
                <input v-model="form.breast_discovery_date" type="date">
              </div>
              <div class="form-field required">
                <div class="label">BI-RADS分级</div>
                <select v-model="form.birads_level">
                  <option>不清楚</option>
                  <option>1</option><option>2</option><option>3</option>
                  <option>4A</option><option>4B</option><option>4C</option>
                  <option>5</option><option>6</option>
                </select>
              </div>
              <div class="form-field">
                <div class="label">数量</div>
                <select v-model="form.nodule_quantity">
                  <option>单发</option>
                  <option>多发</option>
                </select>
              </div>
              <div class="form-field">
                <div class="label">结节大小</div>
                <div class="input-unit">
                  <input v-model="form.nodule_size" placeholder="例如：12.5">
                  <span class="unit">mm</span>
                </div>
              </div>
              <div v-if="String(form.nodule_quantity||'').includes('多发')" class="form-field">
                <div class="label">多发结节个数</div>
                <input v-model="form.nodule_count" type="number" min="1" placeholder="例如：3">
              </div>

              <div class="form-field full">
                <div class="label">结节症状（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in ['无症状','乳房肿块','乳房疼痛','乳房胀满感','乳头溢液','乳房皮肤改变','腋下淋巴结肿大','其他']"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.symptoms||[]).includes(s) }"
                    @click="toggleArr(form.symptoms, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.symptoms||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.symptoms_other" placeholder="请输入其他症状">
                </div>
              </div>

              <div class="form-field full">
                <div class="label">基础疾病史（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in ['无','乳腺增生病史','乳腺纤维瘤病史','乳腺囊肿病史','乳腺炎病史','乳腺癌病史','其他']"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.history||[]).includes(s) }"
                    @click="toggleArr(form.history, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.history||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.breast_disease_history_other" placeholder="请输入其他基础疾病史">
                </div>
              </div>

              <div class="form-field full">
                <div class="label">家族史（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in ['无','一级亲属（父母、子女、亲兄弟姐妹）','二级亲属（伯父、姑妈、舅舅、姨妈、祖父母）','三级亲属（表/堂兄妹）','其他']"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.family_history||[]).includes(s) }"
                    @click="toggleArr(form.family_history, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.family_history||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.family_history_other" placeholder="请输入其他家族史">
                </div>
              </div>

              <div class="form-field full">
                <div class="label">药物使用史（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in ['无','中成药治疗','激素调节药物','维生素辅助治疗','乳腺癌治疗药物','其他']"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.medication_history||[]).includes(s) }"
                    @click="toggleArr(form.medication_history, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.medication_history||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.medication_other" placeholder="请输入其他药物使用史">
                </div>
              </div>
            </div>
          </div>

          <section class="form-sec asset-sec">
            <div class="sec-h"><span class="no">四</span>检查资料上传</div>
            <div class="asset-grid">
              <section class="asset-panel">
                <div class="asset-title">影像报告</div>
                <div class="asset-sub">支持 PDF、JPG、PNG；保存档案后自动关联到当前健康档案。</div>
                <input ref="imagingInputRef" type="file" multiple accept=".pdf,.jpg,.jpeg,.png,image/*" style="display:none" @change="handleImagingFiles">
                <button class="mini-action primary-action" type="button" @click="imagingInputRef?.click()">上传影像报告</button>
                <div class="asset-list">
                  <div v-for="file in imagingFiles" :key="file.key" class="asset-row">
                    <div>
                      <b>{{ file.name }}</b>
                      <span>{{ formatFileSize(file.size) }} · {{ file.uploaded ? '已关联档案' : '待保存上传' }}</span>
                    </div>
                    <button class="asset-link" type="button" @click="removeImagingFile(file.key)">删除</button>
                  </div>
                  <div v-if="!imagingFiles.length" class="asset-empty">暂无影像报告</div>
                </div>
              </section>

              <section class="asset-panel">
                <div class="asset-title">手机舌诊 H5</div>
                <div class="asset-sub">B端只生成手机可访问的舌诊链接；请用患者手机或健康管理师手机打开，电脑和平板不作为采集终端。</div>
                <div class="tongue-h5-panel">
                  <div class="tongue-h5-copy">
                    <input :value="tongueDisplayUrl || '生成后显示手机舌诊链接'" readonly>
                    <button class="asset-link" type="button" @click="copyTongueLink" :disabled="!tongueDisplayUrl">复制链接</button>
                  </div>
                  <div class="tongue-h5-body">
                    <div class="tongue-qr">
                      <img v-if="tongueQrUrl" :src="tongueQrUrl" alt="舌诊H5二维码">
                      <span v-else>生成二维码</span>
                    </div>
                    <div class="tongue-h5-help">
                      <b>手机打开提示</b>
                      <span>生成链接后，用手机扫码或复制链接发送给患者；进入第三方 H5 后在手机内完成舌面图、舌下图采集。</span>
                      <span>检测完成后，结果通过报告回调或报告检索回流到本系统。</span>
                    </div>
                  </div>
                </div>
                <div class="tongue-diagnosis-bar">
                  <button
                    class="mini-action primary-action"
                    type="button"
                    @click="startTongueDiagnosis"
                    :disabled="tongueSubmitting"
                  >
                    {{ tongueSubmitting ? '提交中...' : tongueActionLabel }}
                  </button>
                  <span v-if="tongueTask" class="tongue-status">{{ tongueStatusLabel }}</span>
                </div>
                <div v-if="tongueTask?.tongue_feature" class="tongue-result">
                  {{ tongueTask.tongue_feature }}
                </div>
              </section>
            </div>
          </section>

          <!-- 底部操作行 -->
          <div class="grid-12" style="margin-top:10px">
            <div class="field col-5" style="display:flex;align-items:flex-end;gap:8px">
              <button class="mini-action" type="button" @click="save" :disabled="saving">{{ saving ? '保存中...' : '保存档案' }}</button>
              <button class="mini-action primary-action" type="button" @click="generateReport" :disabled="generating">{{ generating ? reportJobMessage : '生成健康档案' }}</button>
            </div>
          </div>
        </section>
      </div>

      <aside class="record-side">
        <section class="side-card">
          <div class="side-title">建档后流程</div>
          <div class="flow-steps">
            <div class="flow-step done"><span class="dot">1</span><span>建档</span></div>
            <div class="flow-step"><span class="dot">2</span><span>AI解析</span></div>
            <div class="flow-step"><span class="dot">3</span><span>生成健康档案</span></div>
            <div class="flow-step"><span class="dot">4</span><span>审核健康档案</span></div>
            <div class="flow-step"><span class="dot">5</span><span>指定随访任务</span></div>
            <div class="flow-step"><span class="dot">6</span><span>AI随访</span></div>
          </div>
        </section>

        <section class="side-card">
          <div class="side-title">档案预览</div>
          <div class="preview-grid">
            <div class="pv-row"><span class="k">姓名</span><span class="v">{{ form.name || '—' }}</span></div>
            <div class="pv-row"><span class="k">年龄</span><span class="v">{{ form.age || '—' }}</span></div>
            <div class="pv-row"><span class="k">来源</span><span class="v">{{ previewSource }}</span></div>
            <div class="pv-row"><span class="k">结节类型</span><span class="v">{{ visibleNodules.join('、') || '—' }}</span></div>
            <div class="pv-row"><span class="k">科室</span><span class="v">{{ selectedDepartmentName || '—' }}</span></div>
            <div class="pv-row"><span class="k">负责医生</span><span class="v">{{ selectedDoctorName || '—' }}</span></div>
            <div class="pv-row"><span class="k">管理人员</span><span class="v">{{ selectedManagerName || '—' }}</span></div>
          </div>
        </section>

        <section v-if="savedPatientId && savedRecordId" class="side-card saved-card">
          <div class="side-title">已保存</div>
          <div class="preview-grid">
            <div class="pv-row"><span class="k">患者ID</span><span class="v">{{ savedPatientId }}</span></div>
            <div class="pv-row"><span class="k">档案ID</span><span class="v">{{ savedRecordId }}</span></div>
            <div class="pv-row"><span class="k">保存时间</span><span class="v">{{ savedAt || '—' }}</span></div>
          </div>
          <div class="saved-actions">
            <button class="mini-action primary-action" type="button" @click="generateReport" :disabled="generating">
              {{ generating ? reportJobMessage : '基于该档案生成报告' }}
            </button>
            <button class="mini-action" type="button" @click="goPatientList">查看患者列表</button>
          </div>
        </section>

        <section class="side-card">
          <div class="side-title">资料完整度</div>
          <div class="progress">
            <div class="bar"><div class="fill" :style="{ width: `${completeness}%` }"></div></div>
            <div class="muted" style="font-size:12px;margin-top:8px">{{ completeness }}%</div>
          </div>
          <div class="muted" style="font-size:12px;line-height:1.6;margin-top:10px">
            建议优先补全：手机号、出生日期、来源信息、至少选择一种结节类型。
          </div>
        </section>

        <section class="side-card">
          <div class="side-title">下一步提示</div>
          <div class="next-box">
            <div class="next-main">{{ nextTip }}</div>
            <div class="muted" style="font-size:12px;line-height:1.6;margin-top:8px">
            保存后会停留在当前页，确认患者与档案ID后再生成{{ scenario.reportLabel }}。
            </div>
          </div>
        </section>
      </aside>
    </div>

    <!-- 底部操作栏 -->
    <div class="record-foot" v-if="!embedded">
      <button class="btn" type="button" @click="back">取消</button>
      <div style="margin-left:auto;display:flex;gap:8px;align-items:center">
        <div class="more-wrap">
          <button class="btn" type="button" @click="moreOpen = !moreOpen">更多操作 ▾</button>
          <div v-if="moreOpen" class="more-menu">
            <button type="button" @click="toast('保存并上传报告')">保存并上传报告</button>
            <button type="button" @click="toast('保存并发送问卷')">保存并发送问卷</button>
            <button type="button" @click="toast('保存并进入报告处理')">保存并进入报告处理</button>
          </div>
        </div>
        <button class="primary" type="button" @click="save">保存档案</button>
      </div>
    </div>
    </div>

    <ToastMsg ref="toastRef" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import ToastMsg from '../components/ToastMsg.vue'
import { getStoredScenario } from '../config/scenarios'
import { useHospitalApi } from '../composables/useHospitalApi'

const props = defineProps({
  embedded: { type: Boolean, default: false },
  patient: { type: Object, default: null }
})
const emit = defineEmits(['back'])

const router = useRouter()
const toastRef = ref(null)
const user = computed(() => localStorage.getItem('proto_user') || '管理员')
const scenario = computed(() => getStoredScenario())
const hospitalApi = useHospitalApi()
const departments = ref([])
const doctors = ref([])
const managers = ref([])

const moreOpen = ref(false)
const saving = ref(false)
const generating = ref(false)
const reportJobMessage = ref('AI生成中...')
const savedPatientId = ref('')
const savedRecordId = ref('')
const savedAt = ref('')
const savedSnapshot = ref('')
const imagingInputRef = ref(null)
const imagingFiles = ref([])
const uploadedImagingKeys = ref(new Set())
const tongueTask = ref(null)
const tongueH5Url = ref('')
const tongueMobileOpenUrl = ref('')
const tongueSubmitting = ref(false)

const tongueDisplayUrl = computed(() => tongueMobileOpenUrl.value || tongueH5Url.value)

const tongueQrUrl = computed(() => {
  if (!tongueDisplayUrl.value) return ''
  return `https://api.qrserver.com/v1/create-qr-code/?size=180x180&margin=8&data=${encodeURIComponent(tongueDisplayUrl.value)}`
})

const tongueActionLabel = computed(() => {
  if (tongueTask.value?.status === 'h5_sso_created') return '重新打开舌诊 H5'
  if (tongueTask.value?.status === 'completed') return '已完成舌诊'
  return '打开舌诊 H5'
})

const tongueStatusLabel = computed(() => {
  const status = tongueTask.value?.status
  const map = {
    h5_sso_created: 'H5已生成',
    completed: '舌诊已完成',
    failed: '检测失败',
    waiting_inquiry: '待完成'
  }
  return map[status] || status || ''
})

const isImport = computed(() => true)

const organTags = ['肺部结节', '甲状腺结节', '乳腺结节']
const presetTags = [
  { id: 'lung_thyroid', label: '肺+甲' },
  { id: 'lung_breast', label: '肺+乳' },
  { id: 'thyroid_breast', label: '甲+乳' },
  { id: 'triple', label: '三合并' }
]

const familyHistoryOptions = ['无', '一级亲属（父母、子女、亲兄弟姐妹）', '二级亲属（伯父、姑妈、舅舅、姨妈、祖父母）', '三级亲属（表/堂兄妹）', '其他']

const selectedTag = ref('乳腺结节')

const tagToOrgans = {
  '肺部结节': ['肺部结节'],
  '甲状腺结节': ['甲状腺结节'],
  '乳腺结节': ['乳腺结节'],
  'lung_thyroid': ['肺部结节', '甲状腺结节'],
  'lung_breast': ['肺部结节', '乳腺结节'],
  'thyroid_breast': ['甲状腺结节', '乳腺结节'],
  'triple': ['肺部结节', '甲状腺结节', '乳腺结节'],
}

// 结节类型 -> 后端 nodule_type 字段值
const tagToNoduleType = {
  '肺部结节': 'lung',
  '甲状腺结节': 'thyroid',
  '乳腺结节': 'breast',
  'lung_thyroid': 'lung_thyroid',
  'lung_breast': 'breast_lung',
  'thyroid_breast': 'breast_thyroid',
  'triple': 'triple',
}

const noduleTypeToTag = {
  lung: '肺部结节',
  thyroid: '甲状腺结节',
  breast: '乳腺结节',
  lung_thyroid: 'lung_thyroid',
  breast_lung: 'lung_breast',
  lung_breast: 'lung_breast',
  breast_thyroid: 'thyroid_breast',
  thyroid_breast: 'thyroid_breast',
  triple: 'triple',
}

const visibleNodules = computed(() => tagToOrgans[selectedTag.value] || [])

const recordSubtitle = computed(() => {
  const map = {
    hospital: '填写诊疗信息、结节数据与报告资料，完成后可生成健康档案',
    checkup: '填写体检来源、套餐批次、异常指标与筛查结论，完成后可生成体检解读报告',
    pharmacy: '填写药店服务来源、用药情况、慢病标签与健康咨询记录，完成后可生成健康评估报告',
    community: '填写签约信息、网格归属、慢病管理与家庭风险信息，完成后可生成健康管理报告',
  }
  return map[scenario.value.key] || map.hospital
})

const ownerOptions = computed(() => {
  const map = {
    hospital: ['李医生', '王医生', '张医生', '赵医生'],
    checkup: ['体检医生', '总检医生', '健康管理师', '客服专员'],
    pharmacy: ['执业药师', '店长', '慢病专员', '健康顾问'],
    community: ['家庭医生', '公卫医生', '社区护士', '网格员'],
  }
  return map[scenario.value.key] || map.hospital
})

const filteredDoctors = computed(() => {
  if (!form.value.departmentId) return doctors.value
  return doctors.value.filter((doctor) => String(doctor.department_id || '') === String(form.value.departmentId))
})

const selectedDepartmentName = computed(() => departments.value.find((item) => String(item.id) === String(form.value.departmentId))?.name || '')
const selectedDoctorName = computed(() => doctors.value.find((item) => String(item.id) === String(form.value.primaryDoctorId))?.real_name || '')
const selectedManagerName = computed(() => managers.value.find((item) => String(item.id) === String(form.value.managerId))?.real_name || '')

const form = ref({
  // 基础信息
  age: '',
  name: '', gender: '', birthDate: '',
  phone: '', idNo: '', addr: '',
  height: '', weight: '',
  diabetes_history: '无',
  gaofang_address: '',
  emergency: '配偶', emergencyName: '', emergencyPhone: '',
  note: '',
  source: '门诊', dept: '', doctor: '李医生',
  departmentId: '',
  primaryDoctorId: '',
  managerId: '',
  examDate: '',
  batchNo: '',
  visitNo: '', chiefComplaint: '', examType: '超声',
  checkupPackage: '基础筛查套餐', checkupBatch: '', companyName: '', abnormalIndicators: '',
  reportDate: '', reviewAction: '复查预约',
  memberLevel: '普通服务', medicationUse: '', chronicTags: '', consultationType: '用药咨询',
  contractStatus: '已签约', familyDoctorTeam: '', gridName: '', chronicManagement: '无',
  risk: '中风险', needReview: true,

  // 乳腺结节字段（对齐 breast-fields.js）
  breast_discovery_date: '',
  symptoms: [],
  symptoms_other: '',
  birads_level: '不清楚',
  nodule_quantity: '单发',
  nodule_size: '',
  nodule_count: '',
  history: [],
  breast_disease_history_other: '',
  family_history: [],
  family_history_other: '',
  medication_history: [],
  medication_other: '',

  // 甲状腺结节字段
  thyroid_discovery_date: '',
  thyroid_symptoms: [],
  thyroid_symptoms_other: '',
  tirads_level: '不清楚',
  thyroid_nodule_quantity: '',
  thyroid_nodule_size: '',
  thyroid_nodule_count: '',
  hypothyroidism_history: [],
  hypothyroidism_history_other: '',
  thyroid_family_history: [],
  thyroid_family_history_other: '',
  thyroid_medication_history: [],
  thyroid_medication_other: '',

  // 肺部结节字段
  lung_discovery_date: '',
  lung_symptoms: [],
  lung_symptoms_other: '',
  lung_rads_level: '不清楚',
  lung_nodule_quantity: '',
  lung_nodule_size: '',
  lung_nodule_count: '',
  lung_cancer_history: [],
  lung_cancer_history_other: '',
  lung_family_history: [],
  lung_family_history_other: '',
  lung_medication_history: [],
  lung_medication_other: '',
})

watch(
  () => scenario.value.key,
  () => {
    form.value.source = scenario.value.sourceOptions[0] || ''
    form.value.doctor = ownerOptions.value[0] || ''
  },
  { immediate: true }
)

watch(
  () => form.value.departmentId,
  () => {
    if (form.value.primaryDoctorId && !filteredDoctors.value.some((doctor) => String(doctor.id) === String(form.value.primaryDoctorId))) {
      form.value.primaryDoctorId = filteredDoctors.value[0]?.id || ''
    }
  }
)

onMounted(loadHospitalOptions)

async function loadHospitalOptions() {
  try {
    const [deptData, doctorData, managerData] = await Promise.all([
      hospitalApi.getDepartments(),
      hospitalApi.getDoctors(),
      hospitalApi.getManagers(),
    ])
    departments.value = deptData.departments || []
    doctors.value = doctorData.doctors || []
    managers.value = managerData.managers || []
    if (!form.value.departmentId) {
      form.value.departmentId = departments.value.find((item) => item.name === '乳腺科')?.id || departments.value[0]?.id || ''
    }
    if (!form.value.primaryDoctorId) {
      form.value.primaryDoctorId = filteredDoctors.value[0]?.id || doctors.value[0]?.id || ''
    }
    if (!form.value.managerId) {
      form.value.managerId = managers.value[0]?.id || ''
    }
  } catch (e) {
    toast('加载科室和医生失败，请确认后端服务已启动')
  }
}

watch(
  () => form.value.birthDate,
  (birthDate) => {
    form.value.age = calculateAge(birthDate) || ''
  }
)

watch(
  () => props.patient,
  (patient) => {
    if (!props.embedded) return
    if (!patient?.id) {
      form.value.name = ''
      form.value.gender = ''
      form.value.age = ''
      form.value.phone = ''
      savedPatientId.value = ''
      savedRecordId.value = ''
      savedSnapshot.value = ''
      return
    }
    selectedTag.value = noduleTypeToTag[patient.noduleType] || noduleTypeToTag[patient.nodule_type] || '乳腺结节'
    form.value.name = patient.name || ''
    form.value.gender = patient.gender || ''
    form.value.age = patient.age && patient.age !== '—' ? patient.age : ''
    form.value.phone = patient.phone || ''
    form.value.source = patient.source || scenario.value.sourceOptions[0] || ''
    form.value.doctor = patient.owner || ownerOptions.value[0] || ''
    form.value.departmentId = patient.department_id || patient.departmentId || form.value.departmentId
    form.value.primaryDoctorId = patient.primary_doctor_id || patient.primaryDoctorId || form.value.primaryDoctorId
    form.value.managerId = patient.manager_id || patient.managerId || form.value.managerId
    savedPatientId.value = patient._apiId || patient.rawPatientId || patient.id || ''
    savedRecordId.value = patient.workspaceRecordId || patient.rawRecordId || ''
    savedSnapshot.value = ''
  },
  { immediate: true }
)

function calculateAge(birthDate) {
  if (!birthDate) return null
  const birth = new Date(`${birthDate}T00:00:00`)
  if (Number.isNaN(birth.getTime())) return null
  const today = new Date()
  let age = today.getFullYear() - birth.getFullYear()
  const m = today.getMonth() - birth.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age -= 1
  if (age < 0 || age > 130) return null
  return age
}

function toggleOrganType(t) {
  selectedTag.value = t
}

function applyPreset(id) {
  selectedTag.value = id
}

function toggleArr(arr, v) {
  if (!Array.isArray(arr)) return
  const idx = arr.indexOf(v)
  if (idx >= 0) arr.splice(idx, 1)
  else arr.push(v)
}

const activeOrgan = computed(() => {
  const list = visibleNodules.value
  if (list.includes('肺部结节')) return '肺部结节'
  if (list.includes('甲状腺结节')) return '甲状腺结节'
  if (list.includes('乳腺结节')) return '乳腺结节'
  return '乳腺结节'
})

const isLung = computed(() => activeOrgan.value === '肺部结节')
const isThyroid = computed(() => activeOrgan.value === '甲状腺结节')
const isBreast = computed(() => activeOrgan.value === '乳腺结节')

const activeSite = computed({
  get() {
    if (isLung.value) return form.value.lungSite
    if (isThyroid.value) return form.value.thyroidSite
    return form.value.breastSite
  },
  set(v) {
    if (isLung.value) form.value.lungSite = v
    else if (isThyroid.value) form.value.thyroidSite = v
    else form.value.breastSite = v
  }
})

const activeSize = computed({
  get() {
    if (isLung.value) return form.value.lung_nodule_size
    if (isThyroid.value) return form.value.thyroid_nodule_size
    return form.value.nodule_size
  },
  set(v) {
    if (isLung.value) form.value.lung_nodule_size = v
    else if (isThyroid.value) form.value.thyroid_nodule_size = v
    else form.value.nodule_size = v
  }
})

const activeGradeLabel = computed(() => {
  if (isLung.value) return 'Lung-RADS'
  if (isThyroid.value) return 'TI-RADS'
  return 'BI-RADS'
})

const activeGradeOptions = computed(() => {
  if (isLung.value) return ['1类', '2类', '3类', '4A类', '4B类', '4X类']
  if (isThyroid.value) return ['1类', '2类', '3类', '4A类', '4B类', '5类']
  return ['1类', '2类', '3类', '4A类', '4B类', '4C类', '5类']
})

const activeGrade = computed({
  get() {
    if (isLung.value) return form.value.lung_rads_level
    if (isThyroid.value) return form.value.tirads_level
    return form.value.birads_level
  },
  set(v) {
    if (isLung.value) form.value.lung_rads_level = v
    else if (isThyroid.value) form.value.tirads_level = v
    else form.value.birads_level = v
  }
})

const activeAdviceOptions = computed(() => {
  if (isLung.value) return ['建议随访复查', '建议进一步检查', '建议活检']
  if (isThyroid.value) return ['建议随访复查', '建议穿刺活检', '建议手术']
  return ['建议随访复查', '建议穿刺活检', '建议手术']
})

const activeAdvice = computed({
  get() {
    if (isLung.value) return form.value.lungAdvice
    if (isThyroid.value) return form.value.thyroidAdvice
    return form.value.breastAdvice
  },
  set(v) {
    if (isLung.value) form.value.lungAdvice = v
    else if (isThyroid.value) form.value.thyroidAdvice = v
    else form.value.breastAdvice = v
  }
})

const activeSiteOptions = computed(() => {
  if (isLung.value) return ['右上肺', '右中肺', '右下肺', '左上肺', '左下肺']
  if (isThyroid.value) return ['左叶', '右叶', '峡部']
  return ['左乳', '右乳', '双侧']
})

const previewSource = computed(() => {
  const src = form.value.source || ''
  const dept = form.value.dept || ''
  const doc = form.value.doctor || ''
  if (!src && !dept && !doc) return '—'
  return [src, dept, doc].filter(Boolean).join(' · ')
})

const completeness = computed(() => {
  const fields = [
    form.value.name,
    form.value.gender,
    form.value.phone,
    form.value.source,
    visibleNodules.value.length ? 'ok' : ''
  ]
  const total = fields.length
  const done = fields.filter(Boolean).length
  return Math.round((done / total) * 100)
})

const nextTip = computed(() => {
  if (completeness.value < 70) return '建议先补全关键字段，再保存建档。'
  return '可以保存建档，并继续生成健康档案。'
})

function toast(text) {
  moreOpen.value = false
  toastRef.value?.show(text)
}

function fileKey(file) {
  return `${file.name}-${file.size}-${file.lastModified || 0}`
}

function formatFileSize(size) {
  if (!size) return '0KB'
  if (size < 1024 * 1024) return `${Math.max(1, Math.round(size / 1024))}KB`
  return `${(size / 1024 / 1024).toFixed(1)}MB`
}

function handleImagingFiles(event) {
  const files = Array.from(event.target.files || [])
  const existing = new Set(imagingFiles.value.map(f => f.key))
  files.forEach(file => {
    const key = fileKey(file)
    if (existing.has(key)) return
    imagingFiles.value.push({
      key,
      file,
      name: file.name,
      size: file.size,
      uploaded: uploadedImagingKeys.value.has(key)
    })
    existing.add(key)
  })
  event.target.value = ''
}

function removeImagingFile(key) {
  imagingFiles.value = imagingFiles.value.filter(item => item.key !== key)
}

async function startTongueDiagnosis() {
  tongueSubmitting.value = true
  try {
    const { patientId, recordId } = await saveRecordIfNeeded()
    const res = await fetch('/api/b/tongue-diagnosis/h5-sso', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ patient_id: patientId, record_id: recordId })
    })
    const data = await res.json()
    if (!data.success) throw new Error(data.message || 'H5舌诊地址生成失败')
    tongueTask.value = data.data?.task
    tongueH5Url.value = data.data?.h5_url || data.data?.task?.h5_url || ''
    tongueMobileOpenUrl.value = data.data?.mobile_open_url || ''
    if (tongueH5Url.value) window.open(tongueH5Url.value, '_blank', 'noopener')
    toast('手机舌诊链接已生成')
  } catch (e) {
    toast(e.message || 'H5舌诊打开失败')
  } finally {
    tongueSubmitting.value = false
  }
}

async function copyTongueLink() {
  if (!tongueDisplayUrl.value) return
  try {
    await navigator.clipboard.writeText(tongueDisplayUrl.value)
    toast('舌诊链接已复制')
  } catch (e) {
    toast('复制失败，请手动选择链接')
  }
}

async function uploadRecordAssets(recordId) {
  if (!recordId) return
  const pending = imagingFiles.value.filter(item => !uploadedImagingKeys.value.has(item.key))
  if (!pending.length) return

  const formData = new FormData()
  pending.forEach(item => formData.append('imaging_reports', item.file))
  const res = await fetch(`/api/b/records/${recordId}/imaging-reports`, {
    method: 'POST',
    credentials: 'include',
    body: formData
  })
  const data = await res.json()
  if (!data.success) throw new Error('影像报告上传失败：' + (data.message || ''))

  const nextUploaded = new Set(uploadedImagingKeys.value)
  pending.forEach(item => nextUploaded.add(item.key))
  uploadedImagingKeys.value = nextUploaded
  imagingFiles.value = imagingFiles.value.map(item => (
    nextUploaded.has(item.key) ? { ...item, uploaded: true } : item
  ))
}

function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

function back() {
  if (props.embedded) {
    emit('back')
    return
  }
  router.push('/patient')
}

// 将数组字段转为逗号分隔字符串
function arrToStr(v) {
  if (Array.isArray(v)) return v.join(',')
  return v || ''
}

// 构建提交给后端的患者数据
function buildPatientPayload() {
  const f = form.value
  return {
    name: f.name,
    age: f.age ? parseInt(f.age) : null,
    gender: f.gender,
    phone: f.phone,
    nodule_type: tagToNoduleType[selectedTag.value] || 'breast',
    source_channel: f.source || 'manual',
    department_id: f.departmentId || null,
    primary_doctor_id: f.primaryDoctorId || null,
    manager_id: f.managerId || null,
    manager_name: selectedManagerName.value || f.doctor || scenario.value.defaultOwner,
  }
}

// 构建提交给后端的档案数据
function buildRecordPayload() {
  const f = form.value
  return {
    age: f.age ? parseInt(f.age) : null,
    height: f.height ? parseFloat(f.height) : null,
    weight: f.weight ? parseFloat(f.weight) : null,
    phone: f.phone,
    diabetes_history: f.diabetesHistory || f.diabetes_history,
    gaofang_address: f.addr || f.gaofang_address,

    // 乳腺
    breast_discovery_date: f.breast_discovery_date || null,
    birads_level: f.birads_level,
    nodule_quantity: f.nodule_quantity,
    nodule_size: f.nodule_size,
    nodule_count: f.nodule_count,
    symptoms: arrToStr(f.symptoms),
    symptoms_other: f.symptoms_other,
    family_history: arrToStr(f.family_history),
    family_history_other: f.family_history_other,
    breast_family_history: arrToStr(f.family_history),
    breast_family_history_other: f.family_history_other,
    breast_disease_history: arrToStr(f.history),
    breast_disease_history_other: f.breast_disease_history_other,
    medication_history: arrToStr(f.medication_history),
    medication_other: f.medication_other,

    // 甲状腺
    thyroid_discovery_date: f.thyroid_discovery_date || null,
    tirads_level: f.tirads_level,
    thyroid_nodule_quantity: f.thyroid_nodule_quantity,
    thyroid_nodule_size: f.thyroid_nodule_size,
    thyroid_nodule_count: f.thyroid_nodule_count,
    thyroid_symptoms: arrToStr(f.thyroid_symptoms),
    thyroid_symptoms_other: f.thyroid_symptoms_other,
    hypothyroidism_history: arrToStr(f.hypothyroidism_history),
    hypothyroidism_history_other: f.hypothyroidism_history_other,
    thyroid_family_history: arrToStr(f.thyroid_family_history),
    thyroid_family_history_other: f.thyroid_family_history_other,
    thyroid_medication_history: arrToStr(f.thyroid_medication_history),
    thyroid_medication_other: f.thyroid_medication_other,

    // 肺部
    lung_discovery_date: f.lung_discovery_date || null,
    lung_rads_level: f.lung_rads_level,
    lung_nodule_quantity: f.lung_nodule_quantity,
    lung_nodule_size: f.lung_nodule_size,
    lung_nodule_count: f.lung_nodule_count,
    lung_symptoms: arrToStr(f.lung_symptoms),
    lung_symptoms_other: f.lung_symptoms_other,
    lung_cancer_history: arrToStr(f.lung_cancer_history),
    lung_cancer_history_other: f.lung_cancer_history_other,
    lung_family_history: arrToStr(f.lung_family_history),
    lung_family_history_other: f.lung_family_history_other,
    lung_medication_history: arrToStr(f.lung_medication_history),
    lung_medication_other: f.lung_medication_other,
  }
}

function currentRecordSnapshot() {
  return JSON.stringify({
    patient: buildPatientPayload(),
    record: buildRecordPayload(),
    noduleTag: selectedTag.value
  })
}

async function saveRecordIfNeeded() {
  const snapshot = currentRecordSnapshot()
  if (savedPatientId.value && savedRecordId.value && savedSnapshot.value === snapshot) {
    await uploadRecordAssets(savedRecordId.value)
    return {
      patientId: savedPatientId.value,
      recordId: savedRecordId.value,
      reused: true
    }
  }

  if (props.embedded && savedPatientId.value) {
    const recPayload = { ...buildRecordPayload(), patient_id: savedPatientId.value }
    const recRes = await fetch(`/api/b/patients/${savedPatientId.value}/records`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(recPayload)
    })
    const recData = await recRes.json()
    if (!recData.success) throw new Error('保存档案失败：' + (recData.message || ''))
    const recordId = recData.data?.id || recData.data?.record_id

    savedRecordId.value = recordId
    savedAt.value = new Date().toLocaleString('zh-CN', { hour12: false })
    savedSnapshot.value = snapshot
    await uploadRecordAssets(recordId)

    return { patientId: savedPatientId.value, recordId, reused: false }
  }

  const patRes = await fetch('/api/b/patients', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(buildPatientPayload())
  })
  const patData = await patRes.json()
  if (!patData.success) throw new Error('创建患者失败：' + (patData.message || ''))
  const patientId = patData.data.id

  const recPayload = { ...buildRecordPayload(), patient_id: patientId }
  const recRes = await fetch(`/api/b/patients/${patientId}/records`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(recPayload)
  })
  const recData = await recRes.json()
  if (!recData.success) throw new Error('保存档案失败：' + (recData.message || ''))
  const recordId = recData.data?.id || recData.data?.record_id

  savedPatientId.value = patientId
  savedRecordId.value = recordId
  savedAt.value = new Date().toLocaleString('zh-CN', { hour12: false })
  savedSnapshot.value = snapshot
  await uploadRecordAssets(recordId)

  return { patientId, recordId, reused: false }
}

async function save() {
  if (!form.value.name || !form.value.phone) {
    toast('请填写姓名和手机号')
    return
  }
  if (!form.value.departmentId || !form.value.primaryDoctorId || !form.value.managerId) {
    toast('请选择所属科室、主要负责医生和管理人员')
    return
  }
  saving.value = true
  try {
    const result = await saveRecordIfNeeded()
    toast(result.reused ? '档案已保存，无需重复提交' : '档案已保存，请确认后继续生成报告')
  } catch (e) {
    toast(e.message || '网络错误，请确认后端服务已启动')
  } finally {
    saving.value = false
  }
}

async function generateReport() {
  if (!form.value.name || !form.value.phone) {
    toast('请先填写姓名和手机号')
    return
  }
  if (!form.value.departmentId || !form.value.primaryDoctorId || !form.value.managerId) {
    toast('请选择所属科室、主要负责医生和管理人员')
    return
  }
  generating.value = true
  reportJobMessage.value = '提交中...'
  try {
    const { recordId } = await saveRecordIfNeeded()
    reportJobMessage.value = 'AI生成中...'
    toast('报告生成任务已提交，AI处理中...')

    const jobRes = await fetch('/api/b/reports/generate-jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ record_id: recordId })
    })
    const jobData = await jobRes.json()
    if (!jobData.success) {
      toast('提交报告生成任务失败：' + (jobData.message || ''))
      return
    }

    const jobId = jobData.data?.job_id
    if (!jobId) {
      toast('提交报告生成任务失败：未返回任务ID')
      return
    }

    let completed = false
    for (let attempt = 0; attempt < 90; attempt += 1) {
      await wait(attempt < 10 ? 2000 : 5000)
      const statusRes = await fetch(`/api/b/reports/generate-jobs/${jobId}`, {
        credentials: 'include'
      })
      const statusData = await statusRes.json()
      if (!statusData.success) {
        toast('查询报告生成状态失败：' + (statusData.message || ''))
        return
      }

      const status = statusData.data?.status
      const message = statusData.data?.message
      if (status === 'queued') {
        reportJobMessage.value = '排队中...'
      } else if (status === 'running') {
        reportJobMessage.value = 'AI生成中...'
      }
      if (message && attempt % 6 === 0) toast(message)

      if (status === 'completed') {
        completed = true
        toast('健康报告已生成！正在跳转到报告审核页...')
        break
      }

      if (status === 'failed') {
        toast('生成报告失败：' + (message || 'AI生成失败'))
        return
      }
    }

    if (!completed) {
      toast('报告仍在生成中，请稍后到报告审核页查看')
    }

    setTimeout(() => {
      router.push('/patient?tab=review')
    }, 1500)
  } catch (e) {
    toast(e.message || '网络错误，请确认后端服务已启动')
  } finally {
    generating.value = false
    reportJobMessage.value = 'AI生成中...'
  }
}

function goPatientList() {
  router.push('/patient?tab=queue')
}
</script>

<style scoped>
.record-page{height:100%;display:flex;flex-direction:column;overflow:hidden;margin:-16px -20px;background:#f3f6fb;padding:12px}
.record-card{flex:1;min-height:0;border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:auto;display:flex;flex-direction:column}
.record-card-head{display:flex;align-items:center;gap:12px;padding:10px 16px 10px;border-bottom:1px solid #e6edf7;flex-shrink:0}
.record-page-title{font-size:13px;font-weight:950;color:#0f172a}
.record-page-sub{font-size:12px;color:#94a3b8;font-weight:500}
.record-layout{display:grid;grid-template-columns:minmax(0,1fr) 330px;gap:16px;align-items:start;padding:14px 16px;flex:1}
.record-form .form-sec{border:1px solid #e9eff8;border-radius:12px;background:rgba(255,255,255,.92);padding:12px 16px;margin-bottom:10px}
.record-form .sec-h{font-weight:950;color:#0f172a;margin-bottom:6px;display:flex;align-items:center;gap:8px;font-size:12px}
.record-form .sec-h .no{width:20px;height:20px;border-radius:6px;background:#eef5ff;color:#155eef;display:grid;place-items:center;font-size:11px;font-weight:950}
.subsec-h{margin-top:12px;margin-bottom:8px;padding-top:10px;border-top:1px dashed #e6edf7;font-weight:950;color:#0f172a;font-size:12px}
.req::after{content:" *";color:#ef4444;font-weight:900}
.field-label{color:#475569;font-weight:750;font-size:12px;margin-bottom:8px}
.form-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px 12px;align-items:start}
.form-grid.cols3{grid-template-columns:repeat(3,minmax(0,1fr))}
.form-grid.cols4{grid-template-columns:repeat(4,minmax(0,1fr))}
.form-grid .full{grid-column:1 / -1}
.import-hint{display:flex;align-items:flex-start;gap:6px;margin-top:6px;padding:6px 8px;background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;color:#1d4ed8;font-size:11px;line-height:1.45}
.sync-tip{display:flex;align-items:center;gap:6px;margin-top:6px;color:#64748b;font-size:11px}
.sync-tip.after-note{margin-top:6px;line-height:1.35}
.emg-row{display:none}
.nodule-block{display:none}
.nodule-block-title{display:none}
.input-unit{display:flex;gap:8px;align-items:center}
.input-unit input{flex:1}
.unit{color:#64748b;font-size:13px;white-space:nowrap}
.toggle-row{display:flex;align-items:center;gap:10px;height:32px}
.field-row{display:grid;gap:6px;margin-bottom:10px}
.tag-row{display:flex;flex-wrap:wrap;gap:6px}
.tag-btn{border:1px solid #e6edf7;background:#fff;border-radius:999px;padding:3px 10px;color:#475569;font-weight:850;cursor:pointer;font-size:12px;line-height:1.2;display:inline-flex;align-items:center;gap:6px}
.tag-btn.selected{border-color:#93c5fd;background:#f8fbff}
.tag-btn.active{border-color:#155eef;background:#eef5ff;color:#155eef}
.tag-x{font-size:14px;line-height:1;margin-left:2px;color:inherit;opacity:.9}
.tag-divider{width:1px;height:16px;background:#e6edf7;align-self:center;margin:0 2px}
.tag-btn.preset{background:#fff}

.nodule-mini{border:1px solid #eef2f7;border-radius:10px;background:#fbfdff;padding:8px 10px;margin-top:8px}
.nodule-mini-title{font-weight:950;color:#155eef;font-size:12px;margin-bottom:6px}
.asset-sec{background:#f8fbff!important}
.asset-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px}
.asset-panel{border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:12px;min-width:0}
.asset-title{font-weight:950;color:#0f172a;font-size:13px}
.asset-sub{color:#64748b;font-size:12px;line-height:1.5;margin:4px 0 10px}
.asset-list{display:grid;gap:8px;margin-top:10px}
.asset-row{display:flex;align-items:center;justify-content:space-between;gap:10px;border:1px solid #eef2f7;border-radius:10px;background:#fbfdff;padding:8px 10px;min-width:0}
.asset-row b{display:block;font-size:12px;color:#0f172a;max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.asset-row span{display:block;font-size:11px;color:#94a3b8;margin-top:2px}
.asset-link{border:0;background:transparent;color:#155eef;font-weight:900;font-size:12px;cursor:pointer;padding:0}
.asset-link:disabled{color:#cbd5e1;cursor:not-allowed}
.asset-empty{border:1px dashed #dbe5f2;border-radius:10px;padding:10px;color:#94a3b8;font-size:12px;background:#fff}
.tongue-h5-panel{border:1px solid #e6edf7;border-radius:10px;background:#fbfdff;padding:10px;display:grid;gap:10px}
.tongue-h5-copy{display:flex;gap:8px;align-items:center;min-width:0}
.tongue-h5-copy input{height:32px;border:1px solid #dbe5f2;border-radius:8px;background:#fff;padding:0 10px;color:#334155;font-size:12px;min-width:0;flex:1}
.tongue-h5-body{display:grid;grid-template-columns:104px minmax(0,1fr);gap:10px;align-items:center}
.tongue-qr{width:104px;height:104px;border:1px dashed #bfdbfe;border-radius:8px;background:#fff;display:grid;place-items:center;color:#94a3b8;font-size:12px;overflow:hidden}
.tongue-qr img{width:100%;height:100%;object-fit:contain}
.tongue-h5-help{display:grid;gap:5px;color:#64748b;font-size:12px;line-height:1.5}
.tongue-h5-help b{color:#0f172a;font-size:12px}
.tongue-diagnosis-bar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:10px;padding-top:10px;border-top:1px solid #e6edf7}
.tongue-status{font-size:12px;font-weight:850;color:#475569}
.tongue-result{margin-top:8px;border:1px solid #dbeafe;background:#eff6ff;border-radius:8px;padding:8px 10px;color:#1e3a8a;font-size:12px;line-height:1.6;white-space:pre-line}
.upload-zone{border:1px dashed #cbd5e1;border-radius:10px;padding:8px;text-align:center;color:#64748b;background:#fbfdff;font-size:12px}
.file-card2{display:flex;align-items:center;gap:8px;border:1px solid #eef2f7;border-radius:10px;padding:8px 10px;background:#fff}
.file-card2 .fi{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;font-weight:950;color:#fff}
.file-card2 .fi.pdf{background:#ef4444}
.record-foot{position:sticky;bottom:0;left:0;right:0;padding:10px 16px;background:#fff;border-top:1px solid #e6edf7;display:flex;gap:8px;flex-wrap:wrap;align-items:center;z-index:2;flex-shrink:0}
.more-wrap{position:relative}
.more-menu{position:absolute;bottom:calc(100% + 6px);right:0;background:#fff;border:1px solid #e6edf7;border-radius:10px;box-shadow:0 8px 24px rgba(15,23,42,.10);min-width:160px;overflow:hidden;z-index:10}
.more-menu button{display:block;width:100%;padding:10px 14px;text-align:left;border:0;background:transparent;color:#334155;font-weight:850;cursor:pointer;font-size:13px}
.more-menu button:hover{background:#f8fbff;color:#155eef}
.form-field{display:flex;flex-direction:column;gap:5px;min-width:0}
.form-field .label{color:#64748b;font-weight:850;font-size:11px;white-space:nowrap}
.form-field.required .label::after{content:" *";color:#ef4444;font-weight:900}
.form-field.full{grid-column:1 / -1}
.form-field.span-2{grid-column:span 2}

.form-field input,
.form-field select{height:32px;border:1px solid #d9e2ef;border-radius:8px;padding:0 10px;background:#fff;color:#111827;outline:none;font-size:13px;width:100%;box-sizing:border-box;max-width:260px}
.form-field.span-2 input,
.form-field.span-2 select,
.form-field.full input,
.form-field.full select{max-width:none}
.form-field input:focus,
.form-field select:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.10)}
.form-field input:disabled,
.form-field select:disabled{background:#f8fafc;color:#94a3b8;cursor:not-allowed}

.note-box{border:1px solid #d9e2ef;border-radius:10px;padding:8px 10px;display:grid;gap:6px;background:#fff;max-width:none}
.note-box textarea{width:100%;border:0;outline:none;padding:0;resize:none;height:60px;min-height:60px;max-height:68px;font-size:13px;line-height:1.4;color:#111827;background:transparent}
.note-foot{display:flex;align-items:flex-start;gap:10px}
.note-count{margin-left:auto;flex:0 0 auto;font-size:11px;line-height:1.2;white-space:nowrap}
.muted{color:#64748b}
.btn{border:1px solid #d9e2ef;border-radius:10px;background:#fff;color:#475569;padding:7px 12px;font-weight:850;cursor:pointer}
.primary{background:#155eef;border:1px solid #155eef;color:#fff;border-radius:10px;padding:7px 12px;cursor:pointer;font-weight:850}
.tag{display:inline-flex;align-items:center;border-radius:6px;padding:3px 8px;font-size:11px;font-weight:900;line-height:1.4}
.tag.high{background:#fff1f1;color:#dc2626}
.tag.blue{background:#eef5ff;color:#155eef}
.tag.green{background:#ecfff3;color:#14843b}
.toggle{width:36px;height:20px;border-radius:999px;background:#e5e7eb;position:relative;transition:.2s;flex:0 0 auto;cursor:pointer;display:inline-block}
.toggle::after{content:"";position:absolute;left:3px;top:3px;width:16px;height:16px;border-radius:50%;background:#fff;box-shadow:0 2px 6px rgba(15,23,42,.15);transition:.2s}
.toggle.on{background:#155eef}
.toggle.on::after{left:19px}

/* 12列稳定栅格（高密度但可读） */
.grid-12{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:8px 12px;align-items:end}
.col-1{grid-column:span 1}
.col-2{grid-column:span 2}
.col-3{grid-column:span 3}
.col-4{grid-column:span 4}
.col-5{grid-column:span 5}
.col-6{grid-column:span 6}
.field{min-width:0}
.field .label{font-size:12px;color:#64748b;font-weight:900;margin-bottom:6px;white-space:nowrap}
.field.required .label::after{content:" *";color:#ef4444;font-weight:900;margin-left:2px}
.field input,.field select{height:34px;border:1px solid #d9e2ef;border-radius:10px;padding:0 10px;background:#fff;color:#111827;outline:none;font-size:13px;box-sizing:border-box;width:100%}
.field input:focus,.field select:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.10)}
.field.phone input,.field.phone select{min-width:180px}
.field.idno input,.field.idno select{min-width:180px}
.field.addr input,.field.addr select{min-width:260px}
.field.note input,.field.note select{min-width:320px}
.field.dept select{min-width:180px}
.toggle-row{display:flex;align-items:center;gap:8px;height:34px}
.mini-action{height:34px;border:1px solid #d9e2ef;border-radius:10px;background:#fff;color:#155eef;padding:0 10px;font-weight:900;cursor:pointer;width:100%}
.mini-action.ghost{color:#475569}
.mini-action.primary-action{background:#155eef;border-color:#155eef;color:#fff}
.cur-doctor{height:34px;border:1px solid #e6edf7;border-radius:8px;padding:0 10px;background:#f8fafc;color:#334155;font-size:13px;display:flex;align-items:center;font-weight:850}

@media (max-width: 1100px){
  .record-layout{grid-template-columns:minmax(0,1fr)}
  .form-grid.cols4{grid-template-columns:repeat(2,minmax(0,1fr))}
  .form-grid.cols3{grid-template-columns:repeat(2,minmax(0,1fr))}
  .form-field.span-2{grid-column:1 / -1}
  .dense-grid.cols5{grid-template-columns:repeat(2,minmax(180px,1fr))}
  .dense-grid.cols4{grid-template-columns:repeat(2,minmax(180px,1fr))}
}

@media (max-width: 640px){
  .record-page{padding:12px 12px 56px}
  .record-form .form-sec{padding:14px 14px}
  .form-grid.cols4,.form-grid.cols3{grid-template-columns:1fr}
  .form-field.span-2{grid-column:auto}
}

.record-side{position:sticky;top:12px;display:flex;flex-direction:column;gap:10px}
.side-card{background:#fff;border:1px solid #e6edf7;border-radius:12px;box-shadow:0 6px 18px rgba(15,23,42,.04);padding:12px}
.side-title{font-size:12px;font-weight:950;color:#0f172a;margin-bottom:8px}
.flow-steps{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}
.flow-step{display:flex;align-items:center;gap:8px;color:#475569;font-weight:850;font-size:12px;padding:6px 8px;border:1px solid #eef2f7;border-radius:10px;background:#fbfdff}
.flow-step .dot{width:18px;height:18px;border-radius:6px;display:grid;place-items:center;background:#e2e8f0;color:#334155;font-weight:950;font-size:11px}
.flow-step.done .dot{background:#dcfce7;color:#16a34a}
.preview-grid{display:flex;flex-direction:column;gap:8px}
.pv-row{display:flex;justify-content:space-between;gap:10px;font-size:12px}
.pv-row .k{color:#94a3b8;font-weight:850;white-space:nowrap}
.pv-row .v{color:#0f172a;font-weight:900;text-align:right}
.saved-card{border-color:#bfdbfe;background:#f8fbff}
.saved-actions{display:grid;grid-template-columns:1fr;gap:8px;margin-top:10px}
.progress .bar{height:10px;border-radius:999px;background:#eef2f7;overflow:hidden}
.progress .fill{height:100%;background:linear-gradient(90deg,#155eef,#22c55e);border-radius:999px}
.next-box{border:1px solid #eef2f7;background:#fbfdff;border-radius:12px;padding:10px}
.next-main{font-weight:950;color:#0f172a;font-size:12px;line-height:1.45}

/* 高密度横向表单 */
.dense-grid{display:grid;gap:8px 14px;align-items:center}
.dense-grid.cols3{grid-template-columns:repeat(3,minmax(0,1fr))}
.dense-grid.cols4{grid-template-columns:repeat(4,minmax(180px,1fr))}
.dense-grid.cols5{grid-template-columns:repeat(5,minmax(160px,1fr))}
.dense-grid .full{grid-column:1 / -1}
.dense-grid .span-2{grid-column:span 2}
.hfield{display:grid;grid-template-columns:68px minmax(0,1fr);gap:6px;align-items:center;min-width:140px}
.hfield.required .hl::after{content:" *";color:#ef4444;font-weight:900;margin-left:2px}
.hl{color:#64748b;font-weight:900;font-size:12px;white-space:nowrap}
.hfield input,.hfield select{height:32px;border:1px solid #d9e2ef;border-radius:8px;padding:0 10px;background:#fff;color:#111827;outline:none;font-size:13px;box-sizing:border-box;width:100%;min-width:140px}
.hfield input:focus,.hfield select:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.10)}
.hfield.full{grid-column:1 / -1}
.hfield.phone input,.hfield.phone select{min-width:180px}
.hfield.idno input,.hfield.idno select{min-width:180px}
.hfield.addr input,.hfield.addr select{min-width:260px}
.hfield.note input,.hfield.note select{min-width:320px}
.hfield.dept select{min-width:180px}
.hpair{display:flex;align-items:center;gap:8px;min-width:0}
.hpair .grow{flex:1;min-width:0}
.hpair .age{width:86px;flex:0 0 auto}
.unit{color:#64748b;font-size:12px;white-space:nowrap}
.toggle-row{display:flex;align-items:center;gap:8px;height:32px}
</style>
