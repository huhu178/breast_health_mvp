/**
 * 简单的消息提示工具
 * 用于替代 element-plus 的 ElMessage
 */

function showMessage(message, type = 'info') {
  const colors = {
    success: '#67c23a',
    warning: '#e6a23c',
    error: '#f56c6c',
    info: '#409eff'
  }

  const icons = {
    success: '✓',
    warning: '⚠',
    error: '✕',
    info: 'ℹ'
  }

  const messageBox = document.createElement('div')
  messageBox.style.cssText = `
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: white;
    color: ${colors[type]};
    padding: 12px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 9999;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    animation: slideDown 0.3s ease;
  `

  const icon = document.createElement('span')
  icon.style.cssText = `
    font-size: 18px;
    font-weight: bold;
  `
  icon.textContent = icons[type]

  const text = document.createElement('span')
  text.textContent = message

  messageBox.appendChild(icon)
  messageBox.appendChild(text)
  document.body.appendChild(messageBox)

  // 添加动画样式
  if (!document.getElementById('message-animation-style')) {
    const style = document.createElement('style')
    style.id = 'message-animation-style'
    style.textContent = `
      @keyframes slideDown {
        from {
          opacity: 0;
          transform: translateX(-50%) translateY(-20px);
        }
        to {
          opacity: 1;
          transform: translateX(-50%) translateY(0);
        }
      }
    `
    document.head.appendChild(style)
  }

  setTimeout(() => {
    messageBox.style.transition = 'opacity 0.3s ease'
    messageBox.style.opacity = '0'
    setTimeout(() => {
      document.body.removeChild(messageBox)
    }, 300)
  }, 3000)
}

export const Message = {
  success: (message) => showMessage(message, 'success'),
  warning: (message) => showMessage(message, 'warning'),
  error: (message) => showMessage(message, 'error'),
  info: (message) => showMessage(message, 'info')
}

export default Message

