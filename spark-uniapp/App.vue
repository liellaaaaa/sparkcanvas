<script>
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
				// TODO: 检查用户登录状态
				const token = uni.getStorageSync('access_token')
				if (!token) {
					// 未登录，跳转到登录页
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

