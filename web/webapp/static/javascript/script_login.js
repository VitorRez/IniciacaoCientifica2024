function enter(){

    var name = document.getElementById('entrada_nome').value
    var cpf = document.getElementById('entrada_cpf').value
    var eleicao = document.getElementById('entrada_eleicao').value 

    if(name == "vitor" && cpf == "12373075628" && eleicao == "1"){
        alert("Sucesso")
        location.href = "../templates/userpage.html"
    }else{
        alert("Falha")
    }
}