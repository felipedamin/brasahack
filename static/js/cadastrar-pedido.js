$(document).ready(function(){
});

function calcularPedido(){
    data = {}
    lista_input = $('[type="number"]');

    [].forEach.call(lista_input, function(input){
        data[`${input.name}`] = input.value;
    });

    if(String(Object.values(data)).replace(/,/g,'') == ''){
        alert("Preencha a quantidade de produtos, por favor!");
        return false;
    }

    data["nome"] = $('#nome')[0].value;
    data["email"] = $('#email')[0].value;
    data["lat"] = $("#latitude")[0].value;
    data["lon"] = $("#longitude")[0].value;

    $.ajax({
        method: "POST",
        url: "/pedido/",
        data: data,
        success: function(response){
            $("h1")[0].innerText = "Confirme seu pedido"
            $("#lista_bebidas").addClass('d-none');
            $("#painel_confirmacao").removeClass('d-none');
            $(".contact-page__page-title").remove();
            $("html, body").stop().animate({ scrollTop: 0 }, 600, 'swing');

            var num_pedidos = Object.keys(response).length / 3;
            for(i=1; i <= num_pedidos; i++){
                if(i==2){
                    $("#opcao_2").parent().removeClass("d-none");
                    $("#opcao_1 > label")[0].innerText = "Opção 1";
                }
                
                for(j=0;j < Object.keys(response[`pedido${i}`]).length;j++){
                    $(`#opcao_${i}`).append(
                        `
                        <span class="wpcf7-form-control-wrap pedido_${i} d-flex justify-content-between"> 
                            <p style="margin-right:30%;text-align: initial;">${Object.keys(response[`pedido${i}`])[j]}:</p>
                            <p><b>${Object.values(response[`pedido${i}`])[j]}</b></p>
                        </span>
                        <div class="d-none" id="dadosPedido${i}">${JSON.stringify(response[`pedido${i}`])}</div>
                        `                
                    )
                }
    
                $(`#opcao_${i}`).append(
                    `
                    <span class="wpcf7-form-control-wrap pedido_${i} mt-4"> 
                        Com entrega prevista para <b>${response[`entrega${i}`]}</b> e total de <b>R$${response[`total${i}`]}</b>
                    </span>
                    `                
                )

            }
        },
        error: function(response){
            alert('Error!!!!');
        }
    });
}

function confirmarPedido(dados){
 
    $.ajax({
        method: "POST",
        url: "/cadastrar-pedido/",
        data: dados,
        success: function(response){
            toastr.success('Cadastrado com sucesso!');
            setTimeout(() => { window.location.reload(); }, 550);
        },
        error: function(){
            alert('Error, tente novamente!!');
        }
    });
}

function escolherPedido1(){
    confirmarPedido(JSON.parse($("#dadosPedido1")[0].innerText));
}

function escolherPedido2(){
    confirmarPedido(JSON.parse($("#dadosPedido2")[0].innerText));
}
