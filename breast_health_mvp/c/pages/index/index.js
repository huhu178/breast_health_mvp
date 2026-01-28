// index.js
/**
 * @file pages/index/index.js
 * @description 引导式问卷：从B端全字段schema逐题填写，最后提交生成报告
 */

/**
 * @typedef {Object} NoduleTypeOption
 * @property {string} value
 * @property {string} label
 */

/** @type {NoduleTypeOption[]} */
const NODULE_TYPE_OPTIONS = [
  { value: 'breast', label: '乳腺（breast）' },
  { value: 'lung', label: '肺（lung）' },
  { value: 'thyroid', label: '甲状腺（thyroid）' },
  { value: 'breast_lung', label: '乳腺+肺（breast_lung）' },
  { value: 'breast_thyroid', label: '乳腺+甲状腺（breast_thyroid）' },
  { value: 'lung_thyroid', label: '肺+甲状腺（lung_thyroid）' },
  { value: 'triple', label: '三结节（triple）' }
]

/**
 * @description 判断是否为“结节数量（单发/多发）”题目字段名（兼容多版本）
 * @param {string} name
 * @returns {boolean}
 */
function isNoduleQuantityQuestionName(name) {
  return name === 'nodule_quantity' ||
         name === 'nodule_quantity_breast' ||
         name === 'breast_nodule_quantity' ||
         name === 'lung_nodule_quantity' ||
         name === 'thyroid_nodule_quantity'
}

/**
 * @description 获取“结节数量题”对应的大小字段/个数字段（后端最终会兼容 pick_first，但这里统一写入主字段）
 * @param {string} quantityName
 * @returns {{ sizeField: string, countField: string }}
 */
function getNoduleSizeAndCountFields(quantityName) {
  // 肺
  if (String(quantityName).indexOf('lung') >= 0) {
    return { sizeField: 'lung_nodule_size', countField: 'lung_nodule_count' }
  }
  // 甲状腺
  if (String(quantityName).indexOf('thyroid') >= 0) {
    return { sizeField: 'thyroid_nodule_size', countField: 'thyroid_nodule_count' }
  }
  // 乳腺（含 nodule_quantity_breast / breast_nodule_quantity）
  return { sizeField: 'nodule_size', countField: 'nodule_count' }
}

/**
 * @description 校验“结节数量（单发/多发）”题的必填项（大小必填；多发时个数必填）
 * @param {Object} params
 * @param {any} params.currentQuestion
 * @param {Record<string, any>} params.answers
 * @param {any} params.currentValue
 * @returns {boolean}
 */
function validateNoduleQuantityQuestion({ currentQuestion, answers, currentValue }) {
  if (!currentQuestion || !isNoduleQuantityQuestionName(currentQuestion.name)) return true

  if (!currentValue) {
    wx.showToast({ title: '请选择单发或多发', icon: 'none' })
    return false
  }

  const { sizeField, countField } = getNoduleSizeAndCountFields(currentQuestion.name)
  const sizeVal = answers[sizeField]
  const countVal = answers[countField]

  if (sizeVal === null || sizeVal === undefined || String(sizeVal).trim() === '') {
    wx.showToast({ title: '请填写结节大小', icon: 'none' })
    return false
  }

  if (String(currentValue).trim() === '多发') {
    if (countVal === null || countVal === undefined || String(countVal).trim() === '') {
      wx.showToast({ title: '请填写多发结节个数', icon: 'none' })
      return false
    }
  }

  return true
}

Page({
  data: {
    // 基本信息（用户填写）
    apiBaseUrl: '', // 后端地址（从全局读取，用户不可见）
    name: '',
    age: '',
    gender: '', // 性别：男/女
    height: '',
    weight: '',
    phone: '',
    diabetesHistory: '', // 有无糖尿病：无/有
    gaofangAddress: '', // 收货地址
    noduleTypeOptions: NODULE_TYPE_OPTIONS,
    noduleTypeIndex: 0,
    showDebugFields: false, // 是否显示调试字段（开发环境）
    canStart: false, // 是否可以开始问卷
    
    // Schema相关
    isLoadingSchema: false,
    schemaReady: false,
    schemaGroups: [], // 从后端加载的分组
    allQuestions: [], // 扁平化的所有题目（按分组顺序）
    currentIndex: 0, // 当前题目索引
    currentQuestion: null, // 当前题目对象
    currentGroupTitle: '', // 当前分组标题
    totalQuestions: 0,
    
    // 答案存储：fieldName -> value
    answers: {},
    currentValue: null, // 当前题目的值（用于双向绑定，radio/文本等）
    currentCheckedValues: [], // 当前多选的值数组（checkbox-group用）
    currentCheckedValuesStr: '', // 当前多选的字符串形式（用于WXS比较）
    currentCheckedMap: {}, // 当前多选的映射对象（用于快速判断，key是选项值，value是true）
    currentOtherValue: '', // 当前"其他"字段的值
    noduleCountValue: '', // 结节个数（用于组合显示）
    noduleSizeValue: '', // 结节大小（用于组合显示）
    
    // UI状态
    isSubmitting: false,
    errorMessage: '',
    result: null
  },

  /**
   * @description 页面加载：从全局读取默认后端地址
   */
  onLoad() {
    const app = getApp()
    const base = (app && app.globalData && app.globalData.apiBaseUrl) || 'http://127.0.0.1:5000'
    // 开发环境：可以通过设置 showDebugFields = true 显示调试字段
    const showDebug = false // 设置为 true 可显示后端地址输入框（开发调试用）
    this.setData({ 
      apiBaseUrl: base,
      showDebugFields: showDebug
    })
  },

  /**
   * @param {Object} e
   */
  onApiBaseUrlInput(e) {
    const app = getApp()
    this.setData({ apiBaseUrl: e.detail.value })
    if (app && app.globalData) {
      app.globalData.apiBaseUrl = e.detail.value
    }
  },

  /**
   * @param {Object} e
   */
  onPhoneInput(e) {
    this.setData({ phone: e.detail.value })
    this.checkCanStart()
  },

  /**
   * @param {Object} e
   */
  onNameInput(e) {
    this.setData({ name: e.detail.value })
    this.checkCanStart()
  },

  /**
   * @description 性别选择
   */
  onGenderSelect(e) {
    const gender = e.currentTarget.dataset.gender
    this.setData({ gender })
    this.checkCanStart()
  },

  /**
   * @description 检查是否可以开始问卷
   */
  checkCanStart() {
    const { name, age, gender, phone } = this.data
    const canStart = name && name.trim() && 
                     age && age.trim() &&
                     gender && 
                     phone && String(phone).trim().length === 11
    this.setData({ canStart: !!canStart })
  },

  /**
   * @param {Object} e
   */
  onAgeInput(e) {
    this.setData({ age: e.detail.value })
    this.checkCanStart()
  },

  /**
   * @param {Object} e
   */
  onHeightInput(e) {
    this.setData({ height: e.detail.value })
  },

  /**
   * @param {Object} e
   */
  onWeightInput(e) {
    this.setData({ weight: e.detail.value })
  },

  /**
   * @description 糖尿病史选择
   */
  onDiabetesSelect(e) {
    const value = e.currentTarget.dataset.value
    this.setData({ diabetesHistory: value })
  },

  /**
   * @param {Object} e
   */
  onGaofangAddressInput(e) {
    this.setData({ gaofangAddress: e.detail.value })
  },

  /**
   * @param {Object} e
   */
  onNoduleTypeChange(e) {
    const idx = Number(e.detail.value || 0)
    this.setData({ noduleTypeIndex: idx })
    // 切换结节类型时，检查是否可以开始
    this.checkCanStart()
    // 切换结节类型时，重置schema状态
    if (this.data.schemaReady) {
      this.setData({
        schemaReady: false,
        allQuestions: [],
        currentIndex: 0,
        currentQuestion: null,
        answers: {},
        result: null
      })
    }
  },

  /**
   * @description 开始问卷（检查基本信息并加载schema）
   */
  startQuestionnaire() {
    const { name, age, gender, height, weight, phone, diabetesHistory, gaofangAddress } = this.data

    // 校验必填基本信息
    if (!name || !name.trim()) {
      wx.showToast({ title: '请输入姓名', icon: 'none' })
      return
    }
    if (!age || !age.trim()) {
      wx.showToast({ title: '请输入年龄', icon: 'none' })
      return
    }
    if (!gender) {
      wx.showToast({ title: '请选择性别', icon: 'none' })
      return
    }
    if (!phone || String(phone).trim().length !== 11) {
      wx.showToast({ title: '请输入11位手机号', icon: 'none' })
      return
    }

    // 将基本信息保存到answers中（所有字段都保存，包括可选的）
    const basicAnswers = {
      name: name.trim(),
      age: age.trim() ? parseInt(age.trim()) : null,
      gender: gender,
      phone: phone.trim(),
    }
    
    // 可选字段
    if (height && height.trim()) {
      basicAnswers.height = parseFloat(height.trim()) || null
    }
    if (weight && weight.trim()) {
      basicAnswers.weight = parseFloat(weight.trim()) || null
    }
    if (diabetesHistory) {
      basicAnswers.diabetes_history = diabetesHistory
    }
    if (gaofangAddress && gaofangAddress.trim()) {
      basicAnswers.gaofang_address = gaofangAddress.trim()
    }

    this.setData({
      answers: basicAnswers
    })

    // 加载问卷
    this.loadSchema()
  },

  /**
   * @description 从后端加载问卷schema
   */
  loadSchema() {
    const { apiBaseUrl, noduleTypeOptions, noduleTypeIndex } = this.data
    const noduleType = (noduleTypeOptions[noduleTypeIndex] || noduleTypeOptions[0]).value

    if (!apiBaseUrl) {
      // 如果后端地址为空，使用默认值
      const app = getApp()
      const defaultBase = (app && app.globalData && app.globalData.apiBaseUrl) || 'http://127.0.0.1:5000'
      this.setData({ apiBaseUrl: defaultBase })
    }

    this.setData({ isLoadingSchema: true, errorMessage: '' })

    const url = `${apiBaseUrl.replace(/\/+$/, '')}/api/miniprogram/questionnaire/schema?nodule_type=${noduleType}`

    console.log('准备请求问卷schema，URL:', url)
    
    wx.request({
      url,
      method: 'GET',
      header: {
        'content-type': 'application/json'
      },
      success: (res) => {
        console.log('请求成功，状态码:', res.statusCode, '响应:', res.data)
        const body = res.data || {}
        if (body && body.success) {
          const groups = body.data?.groups || []
          // 扁平化所有题目
          const allQuestions = []
          groups.forEach(group => {
            group.fields.forEach(field => {
              allQuestions.push({
                ...field,
                groupId: group.id,
                groupTitle: group.title
              })
            })
          })

          if (allQuestions.length === 0) {
            this.setData({
              errorMessage: '未获取到任何题目，请检查后端schema接口',
              isLoadingSchema: false
            })
            return
          }

          // 初始化第一题
          const firstQ = allQuestions[0]
          this.setData({
            schemaReady: true,
            schemaGroups: groups,
            allQuestions: allQuestions,
            totalQuestions: allQuestions.length,
            currentIndex: 0,
            currentQuestion: firstQ,
            currentGroupTitle: firstQ.groupTitle,
            isLoadingSchema: false
          })
          // 初始化当前值（包括多选和"其他"字段）
          this.initCurrentValue()
        } else {
          const msg = (body && body.message) || `加载失败（HTTP ${res.statusCode}）`
          console.error('请求失败，错误信息:', msg)
          this.setData({ errorMessage: msg, isLoadingSchema: false })
        }
      },
      fail: (err) => {
        console.error('网络请求失败，错误信息:', err)
        const errMsg = err && err.errMsg ? err.errMsg : 'unknown'
        let errorMessage = `网络请求失败：${errMsg}`
        
        // 根据错误类型给出更详细的提示
        if (errMsg.includes('url not in domain list')) {
          errorMessage = '网络请求失败：域名不在白名单中。请在微信开发者工具的"详情" -> "本地设置" -> 勾选"不校验合法域名"'
        } else if (errMsg.includes('timeout')) {
          errorMessage = '网络请求失败：请求超时。请检查后端服务是否运行，地址是否正确'
        } else if (errMsg.includes('fail connect')) {
          errorMessage = '网络请求失败：无法连接到服务器。请检查后端服务是否运行（http://127.0.0.1:5000）'
        }
        
        this.setData({
          errorMessage: errorMessage,
          isLoadingSchema: false
        })
      }
    })
  },

  /**
   * @description 更新当前题目的答案
   */
  updateCurrentAnswer(value) {
    const { currentQuestion, answers } = this.data
    if (!currentQuestion) return

    const newAnswers = { ...answers }
    newAnswers[currentQuestion.name] = value
    this.setData({ answers: newAnswers, currentValue: value })
  },

  /**
   * @description 加载题目时，初始化当前值（包括多选和"其他"字段）
   */
  initCurrentValue() {
    const { currentQuestion, answers } = this.data
    if (!currentQuestion) return

    const savedValue = answers[currentQuestion.name]
    console.log('初始化当前值 - 题目:', currentQuestion.name, '保存的值:', savedValue, '类型:', typeof savedValue)
    
    // 结节数量和大小组合显示的特殊处理
    if (isNoduleQuantityQuestionName(currentQuestion.name)) {
      const { countField, sizeField } = getNoduleSizeAndCountFields(currentQuestion.name)
      const countValue = answers[countField] || ''
      const sizeValue = answers[sizeField] || ''
      this.setData({ 
        currentValue: savedValue !== undefined ? savedValue : null,
        noduleCountValue: countValue,
        noduleSizeValue: sizeValue,
        currentCheckedValues: [],
        currentCheckedValuesStr: '',
        currentCheckedMap: {},
        currentOtherValue: ''
      })
      return
    }
    
    if (currentQuestion.type === 'checkbox-group') {
      // 多选：将保存的值（逗号字符串）转为数组
      let checkedValues = []
      if (savedValue) {
        if (Array.isArray(savedValue)) {
          checkedValues = savedValue.map(v => String(v).trim()).filter(v => v)
        } else if (typeof savedValue === 'string' && savedValue.trim()) {
          checkedValues = savedValue.split(',').map(v => String(v).trim()).filter(v => v)
        }
      }
      console.log('初始化多选值:', checkedValues, '选项:', currentQuestion.options)
      // 使用深拷贝确保数据变化能被检测到
      const checkedValuesCopy = checkedValues.slice()
      const checkedValuesStr = checkedValuesCopy.length > 0 ? checkedValuesCopy.join(',') : ''
      
      // 构建选中映射对象（用于WXML快速判断）
      const checkedMap = {}
      checkedValuesCopy.forEach(v => {
        checkedMap[String(v).trim()] = true
      })
      
      console.log('准备初始化 - checkedValuesStr:', checkedValuesStr, 'checkedValuesCopy:', checkedValuesCopy, 'checkedMap:', checkedMap)
      
      this.setData({ 
        currentCheckedValues: checkedValuesCopy,
        currentCheckedValuesStr: checkedValuesStr,
        currentCheckedMap: checkedMap,
        currentValue: savedValue || '',
        noduleCountValue: '',
        noduleSizeValue: ''
      }, () => {
        console.log('初始化完成后的currentCheckedValues:', this.data.currentCheckedValues)
        console.log('初始化完成后的currentCheckedValuesStr:', this.data.currentCheckedValuesStr)
        console.log('初始化完成后的currentCheckedMap:', this.data.currentCheckedMap)
      })
      
      // 读取"其他"字段的值
      if (currentQuestion.otherField) {
        const otherValue = answers[currentQuestion.otherField] || ''
        this.setData({ currentOtherValue: otherValue })
      } else {
        this.setData({ currentOtherValue: '' })
      }
    } else {
      this.setData({ 
        currentValue: savedValue !== undefined ? savedValue : null,
        currentCheckedValues: [],
        currentCheckedValuesStr: '',
        currentCheckedMap: {},
        currentOtherValue: '',
        noduleCountValue: '',
        noduleSizeValue: ''
      })
    }
  },

  /**
   * @description 单选选择
   */
  onRadioSelect(e) {
    const value = e.currentTarget.dataset.value
    console.log('选择的值:', value)
    this.updateCurrentAnswer(value)
    // 显示反馈
    wx.showToast({ title: '已选择', icon: 'success', duration: 500 })
  },

  /**
   * @description 多选切换
   */
  onCheckboxToggle(e) {
    const value = e.currentTarget.dataset.value
    console.log('多选切换 - 点击的值:', value, '类型:', typeof value)
    console.log('当前选中值:', this.data.currentCheckedValues)
    
    const { currentCheckedValues, currentQuestion, answers } = this.data
    
    // 处理选项值（确保是字符串）
    let optionValue = String(value).trim()
    
    console.log('处理后的选项值:', optionValue)
    
    // 确保数组中的值都是字符串（用于匹配）
    let newCheckedValues = currentCheckedValues.map(v => String(v).trim())
    
    const index = newCheckedValues.indexOf(optionValue)
    
    console.log('选项值:', optionValue, '索引:', index, '当前数组:', newCheckedValues)
    
    if (index > -1) {
      // 取消选择
      newCheckedValues.splice(index, 1)
      console.log('取消选择后:', newCheckedValues)
    } else {
      // 添加选择
      newCheckedValues.push(optionValue)
      console.log('添加选择后:', newCheckedValues)
    }
    
    // 保存主字段（逗号分隔字符串）
    const savedValue = newCheckedValues.length > 0 ? newCheckedValues.join(',') : null
    const newAnswers = { ...answers }
    newAnswers[currentQuestion.name] = savedValue
    
    console.log('保存的值:', savedValue, '更新后的选中值:', newCheckedValues)
    
    // 强制更新，确保界面刷新
    // 使用深拷贝确保数据变化能被检测到
    const updatedCheckedValues = newCheckedValues.slice()
    const checkedValuesStr = updatedCheckedValues.length > 0 ? updatedCheckedValues.join(',') : ''
    
    // 构建选中映射对象（用于WXML快速判断）
    const checkedMap = {}
    updatedCheckedValues.forEach(v => {
      checkedMap[String(v).trim()] = true
    })
    
    console.log('准备更新 - checkedValuesStr:', checkedValuesStr, 'updatedCheckedValues:', updatedCheckedValues, 'checkedMap:', checkedMap)
    
    this.setData({ 
      answers: newAnswers, 
      currentCheckedValues: updatedCheckedValues,
      currentCheckedValuesStr: checkedValuesStr,
      currentCheckedMap: checkedMap,
      currentValue: savedValue || ''
    }, () => {
      console.log('setData完成后的currentCheckedValues:', this.data.currentCheckedValues)
      console.log('setData完成后的currentCheckedValuesStr:', this.data.currentCheckedValuesStr)
      console.log('setData完成后的currentCheckedMap:', this.data.currentCheckedMap)
    })
    
    // 如果取消选择"其他"，清空"其他"字段的值
    if (optionValue === '其他' && index > -1 && currentQuestion.otherField) {
      newAnswers[currentQuestion.otherField] = null
      this.setData({ answers: newAnswers, currentOtherValue: '' })
    }
    
    // 显示反馈
    wx.showToast({ 
      title: newCheckedValues.length > 0 ? '已选择 ' + newCheckedValues.length + ' 项' : '已取消选择', 
      icon: 'success', 
      duration: 800 
    })
  },

  /**
   * @description "其他"输入框输入
   */
  onOtherInput(e) {
    const value = e.detail.value
    const { currentQuestion, answers } = this.data
    
    if (currentQuestion && currentQuestion.otherField) {
      const newAnswers = { ...answers }
      newAnswers[currentQuestion.otherField] = value || null
      this.setData({ answers: newAnswers, currentOtherValue: value })
    }
  },

  /**
   * @description 判断选项是否被选中（用于 WXML）
   */
  isOptionChecked(option) {
    const { currentCheckedValues } = this.data
    if (!currentCheckedValues || !Array.isArray(currentCheckedValues)) {
      return false
    }
    const optionStr = String(option).trim()
    return currentCheckedValues.some(v => String(v).trim() === optionStr)
  },

  /**
   * @param {Object} e
   */
  onValueInput(e) {
    const value = e.detail.value
    this.updateCurrentAnswer(value)
  },

  /**
   * @description 结节个数输入
   */
  onNoduleCountInput(e) {
    const value = e.detail.value
    const { currentQuestion, answers } = this.data
    if (!currentQuestion) return
    
    // 根据当前字段名确定对应的count字段（兼容多版本字段名）
    const { countField } = getNoduleSizeAndCountFields(currentQuestion.name)
    const newAnswers = { ...answers }
    newAnswers[countField] = value || null
    
    this.setData({ 
      answers: newAnswers,
      noduleCountValue: value 
    })
  },

  /**
   * @description 结节大小输入
   */
  onNoduleSizeInput(e) {
    const value = e.detail.value
    const { currentQuestion, answers } = this.data
    if (!currentQuestion) return
    
    // 根据当前字段名确定对应的size字段（兼容多版本字段名）
    const { sizeField } = getNoduleSizeAndCountFields(currentQuestion.name)
    const newAnswers = { ...answers }
    newAnswers[sizeField] = value || null
    
    this.setData({ 
      answers: newAnswers,
      noduleSizeValue: value 
    })
  },

  /**
   * @param {Object} e
   */
  onSwitchChange(e) {
    const value = e.detail.value === true
    this.updateCurrentAnswer(value)
  },

  /**
   * @param {Object} e
   */
  onDateChange(e) {
    const value = e.detail.value
    this.updateCurrentAnswer(value)
  },

  /**
   * @description 上一题
   */
  prevQuestion() {
    const { currentIndex, allQuestions, answers } = this.data
    if (currentIndex <= 0) return

    const prevIdx = currentIndex - 1
    const prevQ = allQuestions[prevIdx]
    this.setData({
      currentIndex: prevIdx,
      currentQuestion: prevQ,
      currentGroupTitle: prevQ.groupTitle
    })
    // 初始化当前值（包括多选和"其他"字段）
    this.initCurrentValue()
  },

  /**
   * @description 下一题
   */
  nextQuestion() {
    const { currentIndex, allQuestions, answers, currentQuestion, currentValue } = this.data
    if (currentIndex >= allQuestions.length - 1) {
      wx.showToast({ title: '已是最后一题，请点击提交', icon: 'none' })
      return
    }

    // 结节数量题：大小/个数必填校验
    if (!validateNoduleQuantityQuestion({ currentQuestion, answers, currentValue })) {
      return
    }

    const nextIdx = currentIndex + 1
    const nextQ = allQuestions[nextIdx]
    this.setData({
      currentIndex: nextIdx,
      currentQuestion: nextQ,
      currentGroupTitle: nextQ.groupTitle
    })
    // 初始化当前值（包括多选和"其他"字段）
    this.initCurrentValue()
  },

  /**
   * @description 跳过当前题目
   */
  skipQuestion() {
    this.updateCurrentAnswer(null)
    // 自动跳到下一题
    setTimeout(() => {
      this.nextQuestion()
    }, 100)
  },

  /**
   * @description 提交所有答案并生成报告
   */
  submitAll() {
    const { apiBaseUrl, phone, name, noduleTypeOptions, noduleTypeIndex, answers } = this.data
    const noduleType = (noduleTypeOptions[noduleTypeIndex] || noduleTypeOptions[0]).value

    // 基础校验
    if (!apiBaseUrl) {
      wx.showToast({ title: '请填写后端地址', icon: 'none' })
      return
    }
    if (!phone || String(phone).trim().length !== 11) {
      wx.showToast({ title: '请输入11位手机号', icon: 'none' })
      return
    }
    if (!name || String(name).trim().length === 0) {
      wx.showToast({ title: '请输入姓名', icon: 'none' })
      return
    }

    // 提交前：对所有“结节数量（单发/多发）”相关字段做一次校验（避免用户跳过后导致缺少大小/个数）
    const quantityNames = [
      'nodule_quantity',
      'nodule_quantity_breast',
      'breast_nodule_quantity',
      'lung_nodule_quantity',
      'thyroid_nodule_quantity'
    ]
    for (let i = 0; i < quantityNames.length; i++) {
      const qName = quantityNames[i]
      if (answers[qName]) {
        const fakeQ = { name: qName }
        if (!validateNoduleQuantityQuestion({ currentQuestion: fakeQ, answers, currentValue: answers[qName] })) {
          return
        }
      }
    }

    // 清理答案：移除空值
    const cleanedAnswers = {}
    Object.keys(answers).forEach(key => {
      const val = answers[key]
      if (val !== null && val !== undefined && val !== '') {
        cleanedAnswers[key] = val
      }
    })

    // 确保包含结节类型
    cleanedAnswers.nodule_type = noduleType

    const url = `${this.data.apiBaseUrl.replace(/\/+$/, '')}/api/miniprogram/questionnaire/submit`
    const payload = {
      phone: cleanedAnswers.phone,
      name: cleanedAnswers.name,
      questionnaire_data: cleanedAnswers
    }

    this.setData({ isSubmitting: true, errorMessage: '', result: null })

    wx.request({
      url,
      method: 'POST',
      header: { 'Content-Type': 'application/json' },
      timeout: 120000,
      data: payload,
      success: (res) => {
        const body = res.data || {}
        if (body && body.success) {
          const d = body.data || {}
          // 业务：报告需健康管理师审核后单独发送给患者（患者不填写健康管理师联系方式）
          const needReviewByManager = !!d.need_manager_contact
          wx.redirectTo({
            url: `/pages/result/result?report_id=${encodeURIComponent(d.report_id || '')}&report_code=${encodeURIComponent(d.report_code || '')}&patient_code=${encodeURIComponent(d.patient_code || '')}&patient_id=${encodeURIComponent(d.patient_id || '')}&need_review=${needReviewByManager ? '1' : '0'}`
          })
        } else {
          const msg = (body && body.message) || `请求失败（HTTP ${res.statusCode}）`
          this.setData({ errorMessage: msg })
          wx.showToast({ title: msg, icon: 'none', duration: 3000 })
        }
      },
      fail: (err) => {
        const errMsg = `网络请求失败：${err && err.errMsg ? err.errMsg : 'unknown'}`
        this.setData({ errorMessage: errMsg })
        wx.showToast({ title: errMsg, icon: 'none', duration: 3000 })
      },
      complete: () => {
        this.setData({ isSubmitting: false })
      }
    })
  }
})
