function enter(){

    const spawner = require('child_process').spawn
    const button_enter = document.getElementById('enter')

    var name = document.getElementById('entrada_nome').value
    var cpf = document.getElementById('entrada_cpf').value
    var eleicao = document.getElementById('entrada_eleicao').value

    const data_to_pass = [name, cpf, eleicao]

    const python_process = spawner('python', ['teste_js.py', JSON.stringify(data_to_pass)])

    python_process.stdout.on('data', (data) => {
        console.log('Data received:', JSON.parse(data.toString()))
    })
    /*if(name == "vitor" && cpf == "12373075628" && eleicao == "1"){
        alert("Sucesso")
        location.href = "../templates/userpage.html"
    }else{
        alert("Falha")
    }*/
}