$(document).ready(function () {
  $('#sendbtn').click(function () {
    // 显示 loading 状态
    showLoading()
    var email = $('input[name="email"]').val()

    var emailPattern = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/
    var isValidEmail = emailPattern.test(email)

    if (isValidEmail) {
      sendEmail(email)
    } else {
      showMessage('error', '邮箱格式不正确或为空。')
    }
  })

  function sendEmail(email) {
    $.ajax({
      url: '/account/register_code',
      type: 'POST',
      data: {
        email: email
      },
      success: function (response) {
        // 关闭 loading 状态
        hideLoading()
        if (response.retcode === 0) {
          showMessage('success', '发送成功', '验证码发送成功，请查收邮箱。')
          startCountdown()
        } else {
          showMessage('error', '发送失败', response.message)
        }
      },
      error: function () {
        // 关闭 loading 状态
        hideLoading()
        showMessage('error', '发送失败', '验证码发送失败，请稍后再试。')
      }
    })
  }

  function showMessage(type, title, text) {
    Swal.fire({
      icon: type,
      title: title,
      text: text,
      timer: 2500,
      showConfirmButton: false
    })
  }

  function showLoading() {
    Swal.fire({
      title: '加载中...',
      allowOutsideClick: false,
      showConfirmButton: false,
      didOpen: () => {
        Swal.showLoading()
      }
    })
  }

  function hideLoading() {
    Swal.close()
  }

  function startCountdown() {
    var countdown = 60
    var $sendBtn = $('#sendbtn')
    var countdownText = $sendBtn.text()

    $sendBtn.prop('disabled', true)

    var countdownTimer = setInterval(function () {
      countdown--

      if (countdown >= 0) {
        $sendBtn.text(countdown + ' S')
      }

      if (countdown === 0) {
        clearInterval(countdownTimer)
        $sendBtn.text(countdownText).prop('disabled', false)
      }
    }, 1000)
  }
})
