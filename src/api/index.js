export default{
    logIn(user, password) {
        return new Promise((resolve,reject) => {
            var respuesta = {codigo: '200'}
            console.log(user, password)
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
