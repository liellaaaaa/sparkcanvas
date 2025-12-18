/**
 * 本地存储工具
 * 封装uni.setStorageSync和uni.getStorageSync
 */

const storage = {
  // 设置存储
  set(key, value) {
    try {
      uni.setStorageSync(key, value)
      return true
    } catch (e) {
      console.error('存储失败:', e)
      return false
    }
  },
  
  // 获取存储
  get(key, defaultValue = null) {
    try {
      const value = uni.getStorageSync(key)
      return value !== '' ? value : defaultValue
    } catch (e) {
      console.error('读取存储失败:', e)
      return defaultValue
    }
  },
  
  // 删除存储
  remove(key) {
    try {
      uni.removeStorageSync(key)
      return true
    } catch (e) {
      console.error('删除存储失败:', e)
      return false
    }
  },
  
  // 清空所有存储
  clear() {
    try {
      uni.clearStorageSync()
      return true
    } catch (e) {
      console.error('清空存储失败:', e)
      return false
    }
  },
  
  // Token相关
  setToken(token) {
    return this.set('access_token', token)
  },
  
  getToken() {
    return this.get('access_token')
  },
  
  removeToken() {
    return this.remove('access_token')
  },
  
  // 用户信息相关
  setUserInfo(userInfo) {
    return this.set('user_info', userInfo)
  },
  
  getUserInfo() {
    return this.get('user_info')
  },
  
  removeUserInfo() {
    return this.remove('user_info')
  }
}

export default storage

