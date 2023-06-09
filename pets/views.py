from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView, Response, status

from groups.models import Group
from traits.models import Trait

from .models import Pet
from .serializers import PetSerializer


class PetView(APIView, PageNumberPagination):
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
            trait_obj = Trait.objects.filter(name__iexact=trait_dict['name']).first()

            if not trait_obj:
                trait_obj = Trait.objects.create(**trait_dict)

            pet_obj.traits.add(trait_obj)

        serializer = PetSerializer(pet_obj)

        return Response(serializer.data, status.HTTP_201_CREATED)

    def get(self, request):
        pets = Pet.objects.all()
        trait = request.query_params.get('trait')

        if trait:
            pets = Pet.objects.filter(traits__name=trait)

        result_page = self.paginate_queryset(pets, request)
        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)


class PetDetailView(APIView):
    def get(self, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(pet)
        return Response(serializer.data)

    def delete(self, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)
        pet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        group = serializer.validated_data.pop('group', None)
        traits = serializer.validated_data.pop('traits', None)

        if group:
            group_obj = Group.objects.filter(
                scientific_name__iexact=group['scientific_name']
            ).first()

            if not group_obj:
                group_obj = Group.objects.create(**group)

            pet.group = group_obj

        if traits:
            pet.traits.clear()
            for trait_dict in traits:
                trait_obj = Trait.objects.filter(
                    name__iexact=trait_dict['name']
                ).first()

                if not trait_obj:
                    trait_obj = Trait.objects.create(**trait_dict)
                
                pet.traits.add(trait_obj)

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)

        pet.save()
        serializer = PetSerializer(pet)

        return Response(serializer.data, status.HTTP_200_OK)
