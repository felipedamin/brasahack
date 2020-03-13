$(document).ready(function(){

});

function calcularPedido(){
    data = {
        nome: $('#nome')[0].value,
        email: $('#email')[0].value,
    }

    lista_input = $('[type="number"]');

    [].forEach.call(lista_input, function(input){
        data[`${input.name}`] = input.value;
    });

    $.ajax({
        method: "POST",
        url: "/pedido/",
        data: data,
        success: function(response){
            // $(".modal-body")[0].innerHTML = `
            //     <p class="age-gate-dialog__question" style="margin-top: 10%;">
            //         O total do seu pedido é de <b style="font-weight:900">R$${response.total}</b> sendo
            //          <b style="font-weight:900">R$${response.frete}</b> de frete com entrega prevista para ${response.prazo}</p>
            //     <p class="age-gate-dialog__question mb-0" style="font-weight:900; font-size:16pt">Confirmar?</p>
            // `;
            $("#lista_bebidas").addClass('d-none');
            $("#painel_confirmacao").removeClass('d-none');
            $(".contact-page__page-title").remove();
            $("html, body").stop().animate({ scrollTop: 0 }, 600, 'swing');

            // IF 2 PEDIDOS TITLE = "TEMOS UMA OUTRA OPÇÃO PARA VOCÊ"
            // IF 1, CONFIRME SEU PEDIDO

            var num_pedidos = Object.keys(response).length / 3;
            for(i=1; i <= num_pedidos; i++){
                if(i==2)
                    $("#opcao_2").parent().removeClass("d-none");
                
                for(j=0;j < Object.keys(response[`pedido${i}`]).length;j++){
                    $(`#opcao_${i}`).append(
                        `
                        <span class="wpcf7-form-control-wrap pedido_${i} d-flex justify-content-between"> 
                            <p style="margin-right:30%;text-align: initial;">${Object.keys(response[`pedido${i}`])[j]}:</p>
                            <p><b>${Object.values(response[`pedido${i}`])[j]}</b></p>
                        </span>
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
            // VERIFICAR SE EXISTE OUTRA OPCAO DE PEDIDO (LENGTH DA RESPONSE)
            // $('[for="pedido_1"]')[0].innerText = "Pedido" 
            // ADICIONAR NO SPAN .PEDIDO_2 LISTA DE BEBIDAS E SUAS QUANTIDADES, TOTAL E ENTREGA
        },
        error: function(response){
            alert('Error!!!!');
        }
    });
}

function confirmarPedido(){
    $.ajax({
        method: "POST",
        url: "/cadastrar-pedido/",
        data: {},
        success: function(response){
            alert('Cadastrado com sucesso!');
        },
        error: function(response){
            alert('Error!!!!');
        }
    });
    $("#exampleModalCenter").modal('hide');
}
