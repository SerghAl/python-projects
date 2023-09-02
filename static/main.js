const form = document.getElementById('upload_form')
const data = new FormData()

const successToast = document.getElementById('success_toast')
const failureToast = document.getElementById('failure_toast')

form.addEventListener('submit', async (e) => {
    e.preventDefault()

    data.append('upload_file', form.elements['upload_file'].files[0])

    const response = await fetch('/projects', {
        method: 'POST',
        body: data,
    })

    let result = await response.json()

    if (result.status === 200) {
        successToast.getElementsByClassName('toast-body')[0].textContent =
            result.msg
        const toastBootstrap = bootstrap.Toast.getOrCreateInstance(successToast)
        toastBootstrap.show()
    } else {
        failureToast.getElementsByClassName('toast-body')[0].textContent =
            result.msg
        const toastBootstrap = bootstrap.Toast.getOrCreateInstance(failureToast)
        toastBootstrap.show()
    }
})
