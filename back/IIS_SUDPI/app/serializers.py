from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Faktura, Dobavljac, Transakcija, Ugovor, Penal

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = get_user_model()
        fields = ['ime_k', 'prz_k', 'mail_k', 'password', 'tip_k']

    def validate_mail_k(self, value):
        if get_user_model().objects.filter(mail_k=value).exists():
            raise serializers.ValidationError("Korisnik sa ovim email-om već postoji.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Lozinka mora imati najmanje 8 karaktera.")
        if value.isdigit():
            raise serializers.ValidationError("Lozinka ne može biti samo numerička.")
        return value

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            username=validated_data['mail_k'],
            ime_k=validated_data['ime_k'],
            prz_k=validated_data['prz_k'],
            mail_k=validated_data['mail_k'],
            password=validated_data['password'],
            tip_k=validated_data['tip_k']
        )
        return user

class DobavljacSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dobavljac
        fields = ['sifra_d', 'naziv']

class FakturaSerializer(serializers.ModelSerializer):
    dobavljac_naziv = serializers.CharField(source='ugovor.dobavljac.naziv', read_only=True)
    dobavljac_id = serializers.IntegerField(source='ugovor.dobavljac.sifra_d', read_only=True)
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Faktura
        fields = [
            'sifra_f', 
            'iznos_f', 
            'datum_prijema_f', 
            'rok_placanja_f', 
            'status_f',
            'status_display',
            'dobavljac_naziv',
            'dobavljac_id'
        ]
    
    def get_status_display(self, obj):
        """Vraća čitljiv naziv statusa"""
        status_mapping = {
            'primljena': 'Primljeno',
            'verifikovana': 'Čeka verifikaciju',
            'isplacena': 'Plaćeno',
            'odbijena': 'Odbačeno'
        }
        return status_mapping.get(obj.status_f, obj.status_f)