export default{
    logIn(user, password) {
        return new Promise((resolve,reject) => {
            var respuesta = {codigo: '200'}
            console.log(user, password)

            var xhr = new XMLHttpRequest()
            xhr.responseType = 'blob'
            var params = url
            xhr.open('POST', 'http://65.108.220.52', true)

            xhr.onload = function () {}
            // respuesta = PETICION DE INICIO DE SESIÓN (user,password)
            if (respuesta.codigo == '200') {
                resolve()
            } else {
                reject()
            }
        })
    },
    register(email, password, name, surname, institution) {
        return new Promise((resolve,reject) => {
            var respuesta = {codigo: '200'}
            console.log(email, password, name, surname, institution)
            // respuesta = PETICION DE REGISTRO (email, password, name, surname, institution)
            if (respuesta.codigo == '200') {
                resolve()
            } else {
                reject()
            }
        })
    }
}
