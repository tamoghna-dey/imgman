from email.mime import image
from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from sinimg.forms import SinImgForm
from sinimg.models import SinImg
from sinimg.helper import blur, color_to_grayscale, clr_to_bw, img_to_pdf
from django.contrib import messages
from django.http import HttpResponseRedirect

CHOICES = [
    {
        'name': "Convert To GrayScale",
        'code': 0
    },
    {
        'name': "Convert To PDF",
        'code': 1
    },
    {
        'name': "Convert To Blur",
        'code': 2
    },
    {
        'name': "Convert To Black And White",
        'code': 3
    }
]

class ProcessImage(View):
    def get(self, request, choice):
        return render(request, "sinimg/process.html")

    def post(self, request, choice):

        id = request.session.get("id")
        obj = SinImg.objects.get(id=id)
        path = obj.img.path

        content_type = "image/png"
        file_name = "demo.png"

        if choice == 0:
            img = color_to_grayscale(path)
        elif choice == 1:
            img = img_to_pdf(path)
            content_type="application/pdf"
            file_name = "demo.pdf"
        elif choice == 2:
            img = blur(path)
        elif choice == 3:
            img = clr_to_bw(path)
        else:
            return HttpResponse("Invalid Option")

        option = request.POST.get("type")

        if option == "Preview":
            image_data = img.getvalue()
            return HttpResponse(image_data, content_type=content_type)
        elif option == "Download":
            return FileResponse(img, as_attachment=True, filename=file_name)
        else:
            return HttpResponse("Invalid Option")

class SelectChoice(View):
    def get(self, request):

        id = request.session.get("id")
        obj = SinImg.objects.get(id=id)
        
        context={
                "object": obj, 
                "choices": CHOICES,
                }

        return render(request, "sinimg/select_choice.html", context)

    # unnecessary POST here, did in frontend
    # def post(self, request):

    #     type = request.POST.get("type")
    #     choice = CHOICES.index(type)
    #     #return #redirect((reverse_lazy("sinimg:process", kwargs={"choice": choice})))
    #     context={
    #         'choice': choice
    #     }
    #     return render(request, "sinimg/select_choice.html", context)

class Upload(View):
    def get(self, request):
        form = SinImgForm()
        context = {
            "form": form,
        }
        return render(request, "sinimg/upload.html", context)
    
    def post(self, request):
        form = SinImgForm(request.POST, request.FILES)

        if form.is_valid():
            obj = form.save()
            request.session['id'] = obj.id     

            return redirect(reverse_lazy("sinimg:select-choice"))
        else:
            messages.warning(request, 'Plese select a Picture')
            return HttpResponseRedirect(request.path)
