from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from quora_app.models import QuestionsAsked, QuestionsAnswered, AnswerVote
from quora_app.forms import AddQuestion, AddAnswer


@login_required
def questions(request):
    """list/filter the questions"""
    try:
        search_value = request.GET.get('search')
        if not search_value:
            qs = QuestionsAsked.objects.all()
        else:
            qs = QuestionsAsked.objects.filter(Q(question__icontains=search_value) | Q(user__username__icontains=search_value) | Q(tag__icontains=search_value))
        all_questions = {
            'questions_list': qs
        }
        if not qs and search_value:
            messages.info(request, 'No data matched!')
        elif not qs:
            messages.info(request, 'No data at this moment!')
    except Exception as e:
        print(f'Error in question listing - {e}')
        all_questions = {}
        messages.error(request, e)
    return render(request, 'questions/home.html', context=all_questions)


@login_required
def ask_question(request):
    """add the question to the db"""
    try:
        if request.method == "POST":
            form = AddQuestion(request.POST, request.FILES)
            if form.is_valid():
                addquestion = form.save(commit=False)
                addquestion.user = request.user
                addquestion.save()
                messages.success(request, 'Question added succefully!')
    except Exception as e:
        print(f"Error in adding question - {e}")
        messages.error(request,e)
    return redirect('questions:home')


@login_required
def question_answer_details(request, question_id):
    """Details of question thread"""
    try:
        qs = QuestionsAsked.objects.filter(id=question_id).first()
        if not qs:
            messages.error(request,'Post does not exits!')
            return redirect('questions:home')
        answer_list = qs.questionsanswered_set.all().order_by('-updated')
        answer_list_len = len(answer_list)
        current_vote_list = [AnswerVote.objects.filter(answer_id=i, user=request.user).first().is_upvote if AnswerVote.objects.filter(answer_id=i, user=request.user).first() else None for i in answer_list.values_list('id', flat=True)]
        print(current_vote_list)
        answer_list = zip(current_vote_list, answer_list)
        return render(request, 'questions/question_answer.html', {'question_data': qs, 'answer_list': answer_list, 'answer_list_len': answer_list_len})
    except Exception as e:
        print(f"Error in question detail - {e}")
        messages.error(request,e)
    return redirect('questions:home')


@login_required
def add_answer(request, question_id):
    """Add answer to the questions"""
    try:
        if request.method == 'POST':
            form = AddAnswer(request.POST, request.FILES)
            if form.is_valid():
                addanswer = form.save(commit=False)
                addanswer.user = request.user
                addanswer.save()
                messages.success(request, 'Comment added succefully!')
    except Exception as e:
        print(f"Error in question details - {e}")
        messages.error(request,e)
    return redirect('questions:answerdetails', question_id=question_id)


@login_required
def answer_vote(request, answer_id):
    """Vote to the answers"""
    question_id=None
    try:
        if request.method == "POST":
            vote_value = request.POST.get('vote_value')
            upvotes_count = 0
            downvotes_count = 0
            if vote_value == 'up_add':
                is_upvote = True
            elif vote_value == 'down_add':
                is_upvote = False
            else:
                is_upvote = None
            if is_upvote not in (True, False):
                return redirect('questions:home')
            questionanswer = QuestionsAnswered.objects.filter(id=answer_id).first()
            question_id = questionanswer.question.id
            answervote = AnswerVote.objects.filter(answer=questionanswer, user=request.user).first()
            if answervote:
                if is_upvote:
                    if answervote.is_upvote:
                        questionanswer.upvotecount -= 1
                        answervote.is_upvote=None
                        answervote.save()
                    else:
                        questionanswer.upvotecount += 1
                        if answervote.is_upvote == False:
                            questionanswer.downvotecount -= 1
                        answervote.is_upvote=True
                        answervote.save()
                elif not is_upvote:
                    if answervote.is_upvote:
                        questionanswer.upvotecount -= 1
                        questionanswer.downvotecount += 1
                        answervote.is_upvote=False
                        answervote.save()
                    else:
                        if answervote.is_upvote == False:
                            questionanswer.downvotecount -= 1
                            answervote.is_upvote = None
                        elif answervote.is_upvote == None:
                            questionanswer.downvotecount += 1
                            answervote.is_upvote = False
                        answervote.save()
                upvotes_count = questionanswer.upvotecount
                downvotes_count = questionanswer.downvotecount
                questionanswer.save()
            else:
                answervote = AnswerVote.objects.create(answer=questionanswer, user=request.user, is_upvote=is_upvote)
                if is_upvote:
                    questionanswer.upvotecount += 1
                elif not is_upvote:
                    questionanswer.downvotecount += 1
                upvotes_count = questionanswer.upvotecount
                downvotes_count = questionanswer.downvotecount
                questionanswer.save()
            return JsonResponse({'upvotes': upvotes_count, 'downvotes': downvotes_count})
    except Exception as e:
        print(f"Error in vote answer - {e}")
        messages.error(request,e)
    if not question_id:
        return redirect('questions:home')
    return redirect('questions:answerdetails', question_id=question_id)