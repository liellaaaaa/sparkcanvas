<script>
	import storage from '@/utils/storage.js'
	
	export default {
		onLaunch: function() {
			console.log('SparkCanvas App Launch')
			// 检查登录状态
			this.checkLoginStatus()
		},
		onShow: function() {
			console.log('SparkCanvas App Show')
		},
		onHide: function() {
			console.log('SparkCanvas App Hide')
		},
		methods: {
			checkLoginStatus() {
				// 检查用户登录状态
				const token = storage.getToken()
				const userInfo = storage.getUserInfo()
				
				if (token && userInfo) {
					console.log('用户已登录:', userInfo)
				} else {
					console.log('用户未登录')
					// 如果需要强制登录，可以取消下面的注释
					// uni.reLaunch({
					// 	url: '/pages/login/login'
					// })
				}
			}
		}
	}
</script>

<style>
	/*每个页面公共css */
	@import './uni.scss';
</style>

