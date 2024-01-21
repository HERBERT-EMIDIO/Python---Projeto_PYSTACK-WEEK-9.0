from django.shortcuts import get_object_or_404, render , redirect
from .models import Categoria, Flashcard, Desafio, FlashcardDesafio
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.contrib.messages import constants 
from django.contrib import messages

# Create your views here.
def novo_flashcard(request):
    # print(request.META) # retorna todos os parâmetros
    # print(request.user) # retorna o usuario logado
    # print(request.user.is_authenticated) # retorna se tiver usuario logado () true or ()false
    
    
    if not request.user.is_authenticated :
        return redirect('/usuarios/logar')
    
    
    if request.method == "GET":
        categorias = Categoria.objects.all()
        #print(categoria) #Português, Matemática
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        
        flashcards = Flashcard.objects.filter(user = request.user)
        
        categoria_filtrar = request.GET.get('categoria')
        dificuldade_filtrar = request.GET.get("dificuldade")
        
        if categoria_filtrar:
            flashcards = flashcards.filter(categoria__id = categoria_filtrar)

        if dificuldade_filtrar:        
            flashcards = flashcards.filter(dificuldade = dificuldade_filtrar)
            
            
        return render(request, 'novo_flashcard.html', {'categorias': categorias, 
                                                       'dificuldades': dificuldades,
                                                       'flashcards': flashcards})
        
    
    elif request.method == "POST":
        pergunta = request.POST.get('pergunta')
        resposta = request.POST.get('resposta')
        categoria = request.POST.get('categoria')
        dificuldade = request.POST.get('dificuldade')
        
        #return HttpResponse(f'{pergunta} - {resposta} - {categoria} - {dificuldade}') 
        
        if len(pergunta.strip()) == 0 or len(resposta.strip()) == 0:
            messages.add_message(request, constants.ERROR, "Preencha os campos de 'Pergunta' e 'Resposta'.")
            return redirect('/flashcard/novo_flashcard/')
        
        #cat = Categoria.objects.filter(id = categoria).first()
        
        flashcard = Flashcard(
            user = request.user,
            pergunta = pergunta,
            resposta = resposta,
            #categoria = cat
            categoria_id = categoria,
            dificuldade = dificuldade, 
        )
        
        
        flashcard.save()
        messages.add_message(request, constants.SUCCESS, "Flashcard 'Cadastrado' com Sucesso.")
        return redirect('/flashcard/novo_flashcard')
    
    
    
def deletar_flashcard(request, id):
    
    flashcard = Flashcard.objects.get(id=id)
    flashcard.delete()
    messages.add_message(
        request, constants.SUCCESS, 'Flashcard deletado com sucesso!'
    )
   
    
    return redirect('/flashcard/novo_flashcard')    



    if request.method == "GET":
        
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        
        return render(request, 'iniciar_desafio.html', {'categorias': categorias,
                                                        'dificuldades':dificuldades})
    
    elif request.method == 'POST':
        titulo = request.POST.get('titulo')
        categorias = request.POST.getlist('categoria')
        dificuldade = request.POST.get('dificuldade')
        qtd_perguntas = request.POST.get('qtd_perguntas')    
        
        
        desafio = Desafio(
            user = request.user,
            titulo = titulo,
            quantidade_perguntas = qtd_perguntas,
            dificuldade = dificuldade,
        )
            
            
        desafio.save()
        '''
        # fazendo em uma linha a penas 
        desafio.categoria.add(*categorias)
        
        '''
        for categoria in categorias:
            #print(categorias)
            desafio.categoria.add(categoria)
            
        
        flashcard = (
            
            Flashcard.objects.filter(user = request.user)
            .filter(dificuldade)
            .filter(categoria_id__in = categorias)
            .order_by('?') # buscar perguntas de forma aleatória    
            
            )

        
        
        # Exercício: Deixar esse codigo de maneira que se tivermos uma quantidade de flashcard menor que a qtd_perguntas não dê erro

        # Resposta: 
        # flashcards = flashcards[: min(flashcard.count(), int(qtd_perguntas))]
        
        if flashcard.count() < int(qtd_perguntas):
            return redirect('/flashcard/iniciar_desafio')
        
        flashcards = flashcards[: int(qtd_perguntas)]
        # flashcards = flashcards[: min(flashcard.count(), int(qtd_perguntas))]
        
        for f in flashcards:
            
            flashcard_desafio = FlashcardDesafio(
                flashcard = f
            )
            
            flashcard_desafio.save()
            desafio.flashcards.add(flashcard_desafio)
        
        desafio.save()    
            
        
        return HttpResponse('Teste')
    


def iniciar_desafio(request):
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        return render(
            request,
            'iniciar_desafio.html',
            {'categorias': categorias,
             'dificuldades': dificuldades},
        )
    elif request.method == 'POST':
        titulo = request.POST.get('titulo')
        categorias = request.POST.getlist('categoria')
        dificuldade = request.POST.get('dificuldade')
        qtd_perguntas = request.POST.get('qtd_perguntas')

        desafio = Desafio(
            user = request.user,
            titulo = titulo,
            quantidade_perguntas = qtd_perguntas,
            dificuldade = dificuldade,
        )
        desafio.save()
        #return HttpResponse('teste')

        #desafio.categoria.add(*categorias)
        
        for categoria in categorias:
            desafio.categoria.add(categoria)

        flashcards = (
            Flashcard.objects.filter(user = request.user)
            .filter(dificuldade = dificuldade)
            .filter(categoria_id__in = categorias)
            .order_by('?') # buscar valores do flashcard aleatório
        )




    
        # Exercício: fazer codigo que resolva a questao de (se tiver menos flashcard do que foi solicitado quat_perguntas)    
        if flashcards.count() < int(qtd_perguntas):
            return redirect('/flashcard/iniciar_desafio/')
        
        flashcards = flashcards[: int(qtd_perguntas)]

        for f in flashcards:
            flashcard_desafio = FlashcardDesafio(
                flashcard=f,
            )
            
            flashcard_desafio.save()
            desafio.flashcards.add(flashcard_desafio)

        desafio.save()

        return redirect(f'/flashcard/desafio/{desafio.id}')           
    
    

def listar_desafio(request):
    desafios = Desafio.objects.filter(user=request.user)
    
    
    #TODO: desenvolver os status
    
    
    #TODO: desenvolver os filtros
    
    #variável necessária
    desafios = Desafio.objects.filter(user=request.user)
    
    # Obtém todas as categorias disponíveis
    categorias = Categoria.objects.all()
    
    # Lógica de filtragem por categoria
    categoria_filtrar = request.GET.get('categoria')
    if categoria_filtrar:
        desafios = desafios.filter(categoria__id=categoria_filtrar)
        
        
    # Lógica de filtragem por dificuldade
    dificuldade_filtrar = request.GET.get('dificuldade')
    if dificuldade_filtrar:
        desafios = desafios.filter(dificuldade=dificuldade_filtrar)
        
    
    # Retorna o resultado filtrado para o template
    return render(request, 'listar_desafio.html', {'desafios': desafios, 'categorias': categorias})    
   

    
    return render(
        request,
        'listar_desafio.html',
        {
            'desafios': desafios,
        },
    )



def desafio(request, id):
    
    desafio = Desafio.objects.get(id=id)
    # Válidação de segurança para identificar se o usuário
    if not desafio.user == request.user:
        raise Http404()



    if request.method == 'GET':
        acertos = desafio.flashcards.filter(respondido = True).filter(acertou = True).count()
        erros = desafio.flashcards.filter(respondido = True).filter(acertou = False).count()
        faltantes = desafio.flashcards.filter(respondido = False).count()
        return render(
            request,
            'desafio.html',
            {
                'desafio': desafio,
                'acertos': acertos,
                'erros': erros,
                'faltantes': faltantes,
            },
        )



def responder_flashcard(request, id):
    flashcard_desafio = FlashcardDesafio.objects.get(id=id)
    acertou = request.GET.get('acertou')
    desafio_id = request.GET.get('desafio_id')


    #Válidação de segurança
    if not flashcard_desafio.flashcard.user == request.user:
        raise Http404()    


    flashcard_desafio.respondido = True
    
    #flashcard_desafio.acertou = True if acertou == '1' else False
    if acertou == "1":
        flashcard_desafio.acertou = True      
    elif acertou =="0":
        flashcard_desafio.acertou = False
    
    
    
    flashcard_desafio.save()
    
    
    return redirect(f'/flashcard/desafio/{desafio_id}/')



def relatorio(request, id):
    desafio = Desafio.objects.get(id=id)


    acertos = desafio.flashcards.filter(acertou=True).count()
    erros = desafio.flashcards.filter(acertou=False).count()

    dados = [acertos, erros]


    categorias = desafio.categoria.all()
    name_categoria = [i.nome for i in categorias]


    dados2 = []
    for categoria in categorias:
        dados2.append(desafio.flashcards.filter(flashcard__categoria = categoria).filter(acertou = True).count())
        
        
   
    #TODO: Fazer o Ranking das matérias

    return render(request, 'relatorio.html', {'desafio': desafio,
                                              'dados': dados,
                                              'categorias': name_categoria,
                                              'dados2': dados2,
                                              },
                  )


    
    
    
    
    
    
    
        
    


"""
# Todo: Desenvolver o Status, e filtros
flashcards = (
        Desafio.objects.filter(user = request.user)
            .filter(dificuldade = dificuldade)
            .filter(categoria_id__in = categorias)
            .order_by('?') # valores do flashcard aleatório
        )
"""    
    
    

"""
# usando o for
#name_categoria = [ i.nome for i in categorias ]
name_categoria =[]
for i in categorias:
    name_categoria.append(i.nome)
    
"""

            
"""
def deletar_flashcard(request, id):
    
    
    # ============================= Início  Exercício=============================================
    # Exercicio: Fazer validação de segurança
    # com o request.user

    # Certifique-se de que o usuário está autenticado
    

    if not request.user.is_authenticated:
        return HttpResponseForbidden("Você não está 'autorizado' a realizar esta ação.")

    # Obtém o flashcard, ou retorna 404 se não existir
    flashcard = get_object_or_404(Flashcard, id=id)

    # Verifica se o usuário tem permissão para deletar o flashcard
    if request.user != flashcard.usuario:
        return HttpResponseForbidden("Você 'não tem permissão' para 'deletar' este flashcard.")


    
    # ============================= Fim =============================================
    
    # return HttpResponse(f'O ID é {id}')    
    flashcard = Flashcard.objects.get(id = id)
    #print(type(flashcard))
    
    flashcard.delete()
    messages.add_message(
        request, constants.SUCCESS, "Flashcard 'deletado' com Sucesso!"
    )
    
    #return HttpResponse('Teste')
    return redirect('/flashcard/novo_flashcard/')

    """       