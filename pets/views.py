from rest_framework.views import APIView, Request, Response, status

from groups.models import Group
from traits.models import Trait

from .models import Pet
from .serializers import PetSerializer


class PetView(APIView):
    def post(self, request):
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = serializer.validated_data.pop('group')
        traits = serializer.validated_data.pop('traits')

        group_obj = Group.objects.filter(
            scientific_name__iexact=group['scientific_name']
        ).first()

        if not group_obj:
            group_obj = Group.objects.create(**group)

        pet_obj = Pet.objects.create(**serializer.validated_data, group=group_obj)

        for trait_dict in traits:
            trait_obj = Trait.objects.filter(
                trait_name__iexact=trait_dict['trait_name']
            ).first()

            if not trait_obj:
                trait_obj = Trait.objects.create(**trait_dict)

            pet_obj.traits.add(trait_obj)

        serializer = PetSerializer(pet_obj)

        return Response(serializer.data, status.HTTP_201_CREATED)
