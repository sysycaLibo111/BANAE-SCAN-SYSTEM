from django import forms
from jsonschema import ValidationError
from .models import  Store, Category, Product, CustomUser, ShippingAddress, StoreValidation
from .supabase_helper import upload_image_to_supabase
import logging
from django.core.exceptions import ValidationError
from supabase import create_client
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from .models import Message
from .models import ShippingFee

import uuid  
import os

logger = logging.getLogger(__name__)

# class CategoryForm(forms.ModelForm):
#     class Meta:
#         model = Category
#         fields = ['name', 'description']
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        
        # Add required attribute and labels
        self.fields['name'].required = True
        self.fields['name'].label = "Category Name"
        self.fields['description'].label = "Description"
        self.fields['description'].required = False
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if self.instance and self.instance.pk:
            if Category.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("A category with this name already exists.")
        else:
            if Category.objects.filter(name=name).exists():
                raise forms.ValidationError("A category with this name already exists.")
        return name
# Old shppinng 
# class ShippingAddressForm(forms.ModelForm):
#     class Meta:
#         model = ShippingAddress
#         fields = ['phone_number', 'address', 'city', 'province', 'zipcode']
#         widgets = {
#             "phone_number": forms.TextInput(attrs={"class": "form-control"}),
#             "address": forms.TextInput(attrs={"class": "form-control"}),
#             "city": forms.TextInput(attrs={"class": "form-control"}),
#             "province": forms.TextInput(attrs={"class": "form-control"}),
#             "zipcode": forms.TextInput(attrs={"class": "form-control"}),
#         }
        

# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = CustomUser    
#         fields = ['first_name', 'last_name', 'username', 'email', 'password', 'image_url']

#     def save(self, commit=True):
#         user = super().save(commit=False)

#         password = self.cleaned_data.get('password')
#         if password:
#             user.set_password(password)  # Hash the password only if it's provided

#         if commit:
#             user.save()

#         # Handle image upload to Supabase
#         image_file = self.cleaned_data.get('image_url')
#         if image_file:
#             print("🔍 Image File Found:", image_file.name)
#             print(f"🔍 Image File Size Before Reading: {image_file.size} bytes")

#             if image_file.size > 0:
#                 image_file.seek(0)
#                 file_data = image_file.read()
#                 print(f"🔍 File Size Before Upload: {len(file_data)} bytes")

#                 supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ROLE_KEY)
#                 bucket_name = "profile-images"
#                 file_name = f"{user.id}_{image_file.name}"

#                 try:
#                     response = supabase.storage.from_(bucket_name).upload(file_name, file_data)

#                     if hasattr(response, 'full_path') and response.full_path:
#                         public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{response.full_path}"
#                         user.image_url = public_url
#                         user.save()
#                         print("✅ Image Uploaded Successfully:", public_url)
#                     else:
#                         print("❌ Error Uploading Image:", response)

#                 except Exception as e:
#                     print(f"⚠️ Exception in upload: {e}")
#             else:
#                 print("❌ File has 0 size, cannot upload image")

#         return user

# class EditProfileForm(UserChangeForm):
    # class Meta:
    #     model = CustomUser
    #     fields = ['first_name', 'last_name', 'username', 'email', 'password', 'image_url']

    # def save(self, commit=True):
    #     user = super().save(commit=False)
        
    #     # If password is changed, hash it
    #     if self.cleaned_data['password']:
    #         user.set_password(self.cleaned_data['password'])

    #     if commit:
    #         user.save()

    #     # Handle image upload to Supabase
    #     image_file = self.cleaned_data.get('image_url')
    #     if image_file:
    #         print("🔍 Image File Found:", image_file.name)  # Debugging output
    #         print(f"🔍 Image File Size Before Reading: {image_file.size} bytes")

    #         if image_file.size > 0:
    #             image_file.seek(0)
    #             file_data = image_file.read()
    #             print(f"🔍 File Size Before Upload: {len(file_data)} bytes")

    #             supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ROLE_KEY)
    #             bucket_name = "profile-images"
    #             file_name = f"{user.id}_{image_file.name}"  # Use username for uniqueness

    #             try:
    #                 response = supabase.storage.from_(bucket_name).upload(file_name, file_data)

    #                 if hasattr(response, 'full_path') and response.full_path:
    #                     # Construct the public URL
    #                     public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{response.full_path}"
    #                     user.image_url = public_url
    #                     user.save()
    #                     print("✅ Image Uploaded Successfully:", public_url)
    #                 else:
    #                     print("❌ Error Uploading Image:", response)

    #             except Exception as e:
    #                 print(f"⚠️ Exception in upload: {e}")
    #         else:
    #             print("❌ File has 0 size, cannot upload image")

    #     return user




class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile information
    """
    password = forms.CharField(
        widget=forms.PasswordInput(), 
        required=False,
        help_text="Leave blank if you don't want to change password"
    )
    
    class Meta:
        model = CustomUser    
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'image_url','role']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.EmailInput(attrs={'class': 'form-control'}),
            'image_url': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)  # Hash the password only if it's provided

        if commit:
            user.save()

        # Handle image upload to Supabase
        image_file = self.cleaned_data.get('image_url')
        if image_file:
            print("🔍 Image File Found:", image_file.name)
            print(f"🔍 Image File Size Before Reading: {image_file.size} bytes")

            if image_file.size > 0:
                image_file.seek(0)
                file_data = image_file.read()
                print(f"🔍 File Size Before Upload: {len(file_data)} bytes")

                supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ROLE_KEY)
                bucket_name = "profile-images"
                file_name = f"{user.id}_{image_file.name}"

                try:
                    # Delete old image if exists
                    try:
                        supabase.storage.from_(bucket_name).remove([f"{user.id}_*"])
                    except:
                        pass  # Ignore if no old image exists
                    
                    response = supabase.storage.from_(bucket_name).upload(file_name, file_data)

                    if hasattr(response, 'full_path') and response.full_path:
                        public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{response.full_path}"
                        user.image_url = public_url
                        user.save()
                        print("✅ Image Uploaded Successfully:", public_url)
                    else:
                        print("❌ Error Uploading Image:", response)

                except Exception as e:
                    print(f"⚠️ Exception in upload: {e}")
            else:
                print("❌ File has 0 size, cannot upload image")

        return user


class ShippingAddressForm(forms.ModelForm):
    """
    Form for updating shipping address
    """
    class Meta:
        model = ShippingAddress
        fields = ['phone_number', 'address', 'city', 'province', 'zipcode', 'is_default']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'province': forms.TextInput(attrs={'class': 'form-control'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EditProfileForm(UserChangeForm):
    """
    Alternative form using UserChangeForm (if needed)
    """
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'image_url']

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # If password is changed, hash it
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        # Handle image upload to Supabase
        image_file = self.cleaned_data.get('image_url')
        if image_file:
            print("🔍 Image File Found:", image_file.name)
            print(f"🔍 Image File Size Before Reading: {image_file.size} bytes")

            if image_file.size > 0:
                image_file.seek(0)
                file_data = image_file.read()
                print(f"🔍 File Size Before Upload: {len(file_data)} bytes")

                supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ROLE_KEY)
                bucket_name = "profile-images"
                file_name = f"{user.id}_{image_file.name}"

                try:
                    response = supabase.storage.from_(bucket_name).upload(file_name, file_data)

                    if hasattr(response, 'full_path') and response.full_path:
                        public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{response.full_path}"
                        user.image_url = public_url
                        user.save()
                        print("✅ Image Uploaded Successfully:", public_url)
                    else:
                        print("❌ Error Uploading Image:", response)

                except Exception as e:
                    print(f"⚠️ Exception in upload: {e}")
            else:
                print("❌ File has 0 size, cannot upload image")

        return user
    


# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['category', 'name', 'description', 'price', 'stock', 'image_url']
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#             'category': forms.Select(attrs={'class': 'form-control'}),
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'price': forms.NumberInput(attrs={'class': 'form-control'}),
#             'stock': forms.NumberInput(attrs={'class': 'form-control'}),
#             'image_url': forms.FileInput(attrs={'class': 'form-control'}),
#         }
    
#     def __init__(self, *args, **kwargs):
#         self.request = kwargs.pop('request', None)
#         super().__init__(*args, **kwargs)
        
#         # Make fields required except image
#         self.fields['category'].required = True
#         self.fields['name'].required = True
#         self.fields['price'].required = True
#         self.fields['stock'].required = True
#         self.fields['image_url'].required = False
        
#         # Filter categories if needed
#         self.fields['category'].queryset = Category.objects.all()
    
#     def clean_price(self):
#         price = self.cleaned_data.get('price')
#         if price is not None and price <= 0:
#             raise ValidationError("Price must be greater than 0")
#         return price
    
#     def clean_stock(self):
#         stock = self.cleaned_data.get('stock')
#         if stock is not None and stock < 0:
#             raise ValidationError("Stock cannot be negative")
#         return stock
    
#     def clean_name(self):
#         name = self.cleaned_data.get('name')
#         if self.instance.pk:  # Editing existing product
#             if Product.objects.exclude(pk=self.instance.pk).filter(
#                 store=self.request.user.store, 
#                 name=name
#             ).exists():
#                 raise ValidationError("A product with this name already exists in your store.")
#         else:  # Creating new product
#             if Product.objects.filter(
#                 store=self.request.user.store, 
#                 name=name
#             ).exists():
#                 raise ValidationError("A product with this name already exists in your store.")
#         return name
    
    
#     def save(self, commit=True):
#         product = super().save(commit=False)
        
#         # Only process image if a new one was uploaded
#         if 'image_url' in self.changed_data:
#             image_file = self.cleaned_data.get('image_url')
#             if image_file:
#                 # Delete old image if exists
#                 if self.instance and self.instance.image_url:
#                     try:
#                         # Extract filename from URL
#                         old_file_path = self.instance.image_url.split('/')[-1]
#                         delete_image_from_supabase(old_file_path)
#                     except Exception as e:
#                         print(f"Error deleting old image: {e}")
                
#                 # Upload new image
#                 try:
#                     supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ROLE_KEY)
#                     bucket_name = "product-images"
#                     file_name = f"{uuid.uuid4()}_{image_file.name}"
                    
#                     # Read file data
#                     image_file.seek(0)
#                     file_data = image_file.read()
                    
#                     # Upload to Supabase
#                     response = supabase.storage.from_(bucket_name).upload(file_name, file_data)
                    
#                     if response:
#                         # Construct public URL
#                         public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{file_name}"
#                         product.image_url = public_url
#                 except Exception as e:
#                     print(f"Error uploading image: {e}")
#                     raise forms.ValidationError("Error uploading product image")
        
#         if commit:
#             product.save()
#             self.save_m2m()
        
#         return product
    
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock', 'image_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image_url': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Make fields required except image
        self.fields['category'].required = True
        self.fields['name'].required = True
        self.fields['price'].required = True
        self.fields['stock'].required = True
        self.fields['image_url'].required = False
        
        # Filter categories if needed
        self.fields['category'].queryset = Category.objects.all()
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise ValidationError("Price must be greater than 0")
        return price
    
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise ValidationError("Stock cannot be negative")
        return stock
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        
        # Safe check for request and user
        if not self.request or not hasattr(self.request, 'user') or not self.request.user.is_authenticated:
            raise ValidationError("User authentication required to validate product name.")
        
        # Check if user has a store
        if not hasattr(self.request.user, 'store'):
            raise ValidationError("User store not found.")
        
        store = self.request.user.store
        
        if self.instance.pk:  # Editing existing product
            if Product.objects.exclude(pk=self.instance.pk).filter(
                store=store, 
                name=name
            ).exists():
                raise ValidationError("A product with this name already exists in your store.")
        else:  # Creating new product
            if Product.objects.filter(
                store=store, 
                name=name
            ).exists():
                raise ValidationError("A product with this name already exists in your store.")
        return name
    
    def save(self, commit=True):
        product = super().save(commit=False)
        
        # Only process image if a new one was uploaded
        if 'image_url' in self.changed_data:
            image_file = self.cleaned_data.get('image_url')
            if image_file:
                # Delete old image if exists
                if self.instance and self.instance.image_url:
                    try:
                        # Extract filename from URL
                        old_file_path = self.instance.image_url.split('/')[-1]
                        delete_image_from_supabase(old_file_path)
                    except Exception as e:
                        print(f"Error deleting old image: {e}")
                
                # Upload new image
                try:
                    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ROLE_KEY)
                    bucket_name = "product-images"
                    file_name = f"{uuid.uuid4()}_{image_file.name}"
                    
                    # Read file data
                    image_file.seek(0)
                    file_data = image_file.read()
                    
                    # Upload to Supabase
                    response = supabase.storage.from_(bucket_name).upload(file_name, file_data)
                    
                    if response:
                        # Construct public URL
                        public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{file_name}"
                        product.image_url = public_url
                except Exception as e:
                    print(f"Error uploading image: {e}")
                    raise forms.ValidationError("Error uploading product image")
        
        if commit:
            product.save()
            self.save_m2m()
        
        return product

# class StoreValidationForm(forms.ModelForm):
#     id_picture = forms.ImageField(
#         required=True,
#         widget=forms.FileInput(attrs={'class': 'form-control'})
#     )

#     class Meta:
#         model = StoreValidation
#         fields = [
#             'first_name',
#             'last_name',
#             'phone_number',
#             'address',
#             'city',
#             'province',
#             'id_picture',
#         ]
#         widgets = {
#             'first_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'last_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
#             'address': forms.TextInput(attrs={'class': 'form-control'}),
#             'city': forms.TextInput(attrs={'class': 'form-control'}),
#             'province': forms.TextInput(attrs={'class': 'form-control'}),
#         }

#     def clean_phone_number(self):
#         phone_number = self.cleaned_data.get('phone_number')
#         # Allow phone numbers with +, -, spaces, and digits
#         cleaned = ''.join(filter(str.isdigit, phone_number))
#         if len(cleaned) < 10:
#             raise ValidationError("Phone number must be at least 10 digits.")
#         return phone_number

#     # def save(self, commit=True, user=None):
#     #     instance = super().save(commit=False)
        
#     #     # Set the user if provided
#     #     if user:
#     #         instance.store_owner = user
        
#     #     id_picture = self.cleaned_data.get('id_picture')

#     #     if id_picture:
#     #         try:
#     #             supabase = create_client(
#     #                 settings.SUPABASE_URL,
#     #                 settings.SUPABASE_ROLE_KEY
#     #             )
#     #             bucket_name = "store-validations"

#     #             # Generate unique filename
#     #             file_ext = os.path.splitext(id_picture.name)[1]
#     #             user_id = user.id if user else 'unknown'
#     #             file_name = f"id_{user_id}_{uuid.uuid4()}{file_ext}"

#     #             # Read file data
#     #             id_picture.seek(0)
#     #             file_data = id_picture.read()

#     #             # Upload to Supabase
#     #             result = supabase.storage.from_(bucket_name).upload(
#     #                 path=file_name,
#     #                 file=file_data,
#     #                 file_options={"content-type": id_picture.content_type}
#     #             )

#     #             print("Upload Response:", result)

#     #             # Get public URL
#     #             public_url = (
#     #                 f"{settings.SUPABASE_URL}/storage/v1/object/public/"
#     #                 f"{bucket_name}/{file_name}"
#     #             )
#     #             print("✅ Public URL:", public_url)
#     #             instance.id_picture = public_url

#     #         except Exception as e:
#     #             print(f"Error uploading ID picture: {str(e)}")
#     #             raise ValidationError(f"Error uploading ID picture: {str(e)}")

#     #     if commit:
#     #         instance.save()
#     #     return instance
#     def save(self, commit=True, user=None):
#         instance = super().save(commit=False)

#         if user:
#             instance.store_owner = user

#         id_picture = self.cleaned_data.get('id_picture')

#         if id_picture:
#             try:
#                 # Reset file pointer
#                 id_picture.seek(0)

#                 # Validate file size (e.g., 5MB max)
#                 if id_picture.size > 5 * 1024 * 1024:
#                     raise ValidationError("Image file too large ( > 5MB )")

#                 # Validate file type
#                 allowed_types = ['image/jpeg', 'image/png', 'image/gif']
#                 if id_picture.content_type not in allowed_types:
#                     raise ValidationError("Only JPEG, PNG and GIF images are allowed")

#                 supabase = create_client(
#                     settings.SUPABASE_URL,
#                     settings.SUPABASE_ROLE_KEY
#                 )
#                 bucket_name = "store-validations"

#                 # Generate unique filename
#                 file_ext = os.path.splitext(id_picture.name)[1].lower()
#                 user_id = user.id if user else 'unknown'
#                 file_name = f"id_{user_id}_{uuid.uuid4()}{file_ext}"

#                 # Upload to Supabase
#                 result = supabase.storage.from_(bucket_name).upload(
#                     path=file_name,
#                     file=id_picture.read(),
#                     file_options={"content-type": id_picture.content_type}
#                 )

#                 # Check if upload was successful
#                 if hasattr(result, 'error') and result.error:
#                     raise Exception(f"Supabase upload error: {result.error}")

#                 # Construct public URL
#                 public_url = (
#                     f"{settings.SUPABASE_URL}/storage/v1/object/public/"
#                     f"{bucket_name}/{file_name}"
#                 )
#                 instance.id_picture = public_url

#             except Exception as e:
#                 print(f"Error uploading ID picture: {str(e)}")
#                 raise ValidationError(f"Error uploading ID picture: {str(e)}")

#         if commit:
#             instance.save()
#         return instance




#    # def save(self, commit=True, user=None):
#     #     instance = super().save(commit=False)
        
#     #     # Set the user if provided
#     #     if user:
#     #         instance.store_owner = user
        
#     #     id_picture = self.cleaned_data.get('id_picture')

#     #     if id_picture:
#     #         try:
#     #             supabase = create_client(
#     #                 settings.SUPABASE_URL,
#     #                 settings.SUPABASE_ROLE_KEY
#     #             )
#     #             bucket_name = "store-validations"

#     #             # Generate unique filename
#     #             file_ext = os.path.splitext(id_picture.name)[1]
#     #             user_id = user.id if user else 'unknown'
#     #             file_name = f"id_{user_id}_{uuid.uuid4()}{file_ext}"

#     #             # Read file data
#     #             id_picture.seek(0)
#     #             file_data = id_picture.read()

#     #             # Upload to Supabase
#     #             result = supabase.storage.from_(bucket_name).upload(
#     #                 path=file_name,
#     #                 file=file_data,
#     #                 file_options={"content-type": id_picture.content_type}
#     #             )

#     #             print("Upload Response:", result)

#     #             # Get public URL
#     #             public_url = (
#     #                 f"{settings.SUPABASE_URL}/storage/v1/object/public/"
#     #                 f"{bucket_name}/{file_name}"
#     #             )
#     #             print("✅ Public URL:", public_url)
#     #             instance.id_picture = public_url

#     #         except Exception as e:
#     #             print(f"Error uploading ID picture: {str(e)}")
#     #             raise ValidationError(f"Error uploading ID picture: {str(e)}")

#     #     if commit:
#     #         instance.save()
#     #     return instance

class StoreValidationForm(forms.ModelForm):
    id_picture = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = StoreValidation
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'address',
            'city',
            'province',
            'id_picture',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'province': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Allow phone numbers with +, -, spaces, and digits
        cleaned = ''.join(filter(str.isdigit, phone_number))
        if len(cleaned) < 10:
            raise ValidationError("Phone number must be at least 10 digits.")
        return phone_number

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        
        # Set the user if provided
        if user:
            instance.store_owner = user
        
        id_picture = self.cleaned_data.get('id_picture')

        if id_picture:
            try:
                supabase = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_ROLE_KEY
                )
                bucket_name = "id-pictures"

                # Generate unique filename
                file_ext = os.path.splitext(id_picture.name)[1]
                user_id = user.id if user else 'unknown'
                file_name = f"id_{user_id}_{uuid.uuid4()}{file_ext}"

                # Read file data
                id_picture.seek(0)
                file_data = id_picture.read()

                # Upload to Supabase
                result = supabase.storage.from_(bucket_name).upload(
                    path=file_name,
                    file=file_data,
                    file_options={"content-type": id_picture.content_type}
                )

                print("Upload Response:", result)

                # Get public URL
                public_url = (
                    f"{settings.SUPABASE_URL}/storage/v1/object/public/"
                    f"{bucket_name}/{file_name}"
                )
                print("✅ Public URL:", public_url)
                instance.id_picture = public_url

            except Exception as e:
                print(f"Error uploading ID picture: {str(e)}")
                raise ValidationError(f"Error uploading ID picture: {str(e)}")

        if commit:
            instance.save()
        return instance



# 1st
# class StoreForm(forms.ModelForm):
#     class Meta:
#         model = Store
#         fields = ['name', 'description', 'logo', 'address', 'city', 'province', 'is_active']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#             'logo': forms.FileInput(attrs={'class': 'form-control'}),
#             'address': forms.TextInput(attrs={'class': 'form-control'}),
#             'city': forms.TextInput(attrs={'class': 'form-control'}),
#             'province': forms.TextInput(attrs={'class': 'form-control'}),
#             'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }
    
#     def __init__(self, *args, **kwargs):
#         self.request = kwargs.pop('request', None)
#         super().__init__(*args, **kwargs)
#         self.fields['logo'].required = False
    
#     def clean_name(self):
#         name = self.cleaned_data.get('name')
#         query = Store.objects.exclude(owner=self.request.user).filter(name__iexact=name)
#         if self.instance and self.instance.pk:
#             query = query.exclude(pk=self.instance.pk)
#         if query.exists():
#             raise ValidationError("A store with this name already exists.")
#         return name
    
#     def save(self, commit=True):
#         store = super().save(commit=False)
#         store.owner = self.request.user
        
#         logo_file = self.cleaned_data.get('logo')
#         if logo_file and hasattr(logo_file, 'file'):
#             try:
#                 supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ROLE_KEY)
#                 bucket_name = "store-logos"
                
#                 # Generate unique filename
#                 file_ext = os.path.splitext(logo_file.name)[1]
#                 file_name = f"logo_{uuid.uuid4()}{file_ext}"
                
#                 # Read file content
#                 logo_file.seek(0)
#                 file_content = logo_file.read()
                
#                 # Upload to Supabase
#                 supabase.storage.from_(bucket_name).upload(
#                     file_name, 
#                     file_content,
#                     {"content-type": logo_file.content_type}
#                 )
                
#                 # Get public URL
#                 public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{file_name}"
#                 store.logo = public_url
                
#                 # Delete old logo if exists
#                 if self.instance and self.instance.logo:
#                     try:
#                         old_file_name = self.instance.logo.split('/')[-1]
#                         supabase.storage.from_(bucket_name).remove([old_file_name])
#                     except Exception as e:
#                         print(f"Error deleting old logo: {e}")
                        
#             except Exception as e:
#                 print(f"Error uploading logo: {e}")
#                 raise forms.ValidationError("Error uploading store logo")
#         elif 'logo-clear' in self.data and self.instance and self.instance.logo:
#             # Handle logo removal if clear checkbox is checked
#             try:
#                 supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ROLE_KEY)
#                 bucket_name = "store-logos"
#                 old_file_name = self.instance.logo.split('/')[-1]
#                 supabase.storage.from_(bucket_name).remove([old_file_name])
#                 store.logo = None
#             except Exception as e:
#                 print(f"Error deleting logo: {e}")
#         else:
#             # Keep old logo if no new file is uploaded
#             if self.instance and self.instance.logo:
#                 store.logo = self.instance.logo

#         if commit:
#             store.save()
        
#         return store



class StoreForm(forms.ModelForm):
    # Make logo optional and add a clear checkbox
    logo_clear = forms.BooleanField(required=False, label='Remove current logo')
    
    class Meta:
        model = Store
        fields = ['name', 'description', 'logo', 'address', 'city', 'province', 'latitude', 'longitude']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your store name'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Describe your store...'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'province': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Province'
            }),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Make logo field not required
        self.fields['logo'].required = False
        
        # Make latitude/longitude not required (can be added later)
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        
        # Add help text
        self.fields['logo'].help_text = 'Upload a logo for your store (optional, max 5MB)'
        
        # If editing existing store, show current logo status
        if self.instance and self.instance.pk and self.instance.logo:
            self.fields['logo'].help_text = 'Leave blank to keep current logo, or upload new one to replace it'
    
    def clean_name(self):
        """Validate that store name is unique (excluding current store if editing)"""
        name = self.cleaned_data.get('name')
        
        if not name:
            raise ValidationError("Store name is required.")
        
        # Check for duplicate names (case-insensitive)
        query = Store.objects.filter(name__iexact=name)
        
        # If editing, exclude current store from check
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        
        # Also exclude stores owned by current user (if updating)
        if self.request and self.request.user:
            query = query.exclude(owner=self.request.user)
        
        if query.exists():
            raise ValidationError("A store with this name already exists. Please choose a different name.")
        
        return name
    
    def clean_logo(self):
        """Validate logo file"""
        logo = self.cleaned_data.get('logo')
        
        if logo and hasattr(logo, 'size'):
            # Check file size (max 5MB)
            if logo.size > 5 * 1024 * 1024:
                raise ValidationError("Logo file size must be less than 5MB.")
            
            # Check file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            ext = os.path.splitext(logo.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError("Please upload a valid image file (JPG, PNG, or GIF).")
        
        return logo
    
    def save(self, commit=True):
        """Save store with logo upload to Supabase"""
        store = super().save(commit=False)
        
        # Set owner if not already set
        if not store.owner_id and self.request:
            store.owner = self.request.user
        
        # Handle logo upload
        logo_file = self.cleaned_data.get('logo')
        logo_clear = self.cleaned_data.get('logo_clear', False)
        
        # If user wants to clear the logo
        if logo_clear and self.instance and self.instance.logo:
            try:
                supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ROLE_KEY)
                bucket_name = "store-logos"
                old_file_name = self.instance.logo.split('/')[-1]
                supabase.storage.from_(bucket_name).remove([old_file_name])
                print(f"✅ Old logo deleted: {old_file_name}")
            except Exception as e:
                print(f"⚠️ Error deleting old logo: {e}")
            
            store.logo = None
        
        # If new logo file is uploaded
        elif logo_file and hasattr(logo_file, 'file'):
            try:
                supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ROLE_KEY)
                bucket_name = "store-logos"
                
                # Delete old logo if it exists
                if self.instance and self.instance.logo:
                    try:
                        old_file_name = self.instance.logo.split('/')[-1]
                        supabase.storage.from_(bucket_name).remove([old_file_name])
                        print(f"✅ Old logo deleted: {old_file_name}")
                    except Exception as e:
                        print(f"⚠️ Error deleting old logo: {e}")
                
                # Generate unique filename
                file_ext = os.path.splitext(logo_file.name)[1]
                file_name = f"logo_{uuid.uuid4()}{file_ext}"
                
                # Read file content
                logo_file.seek(0)
                file_content = logo_file.read()
                
                # Upload to Supabase
                result = supabase.storage.from_(bucket_name).upload(
                    file_name,
                    file_content,
                    {"content-type": logo_file.content_type}
                )
                
                print(f"✅ Logo uploaded: {file_name}")
                
                # Get public URL
                public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{file_name}"
                store.logo = public_url
                
                print(f"✅ Logo URL: {public_url}")
                
            except Exception as e:
                print(f"❌ Error uploading logo: {e}")
                traceback.print_exc()
                raise forms.ValidationError(f"Error uploading store logo: {str(e)}")
        
        # If no new file and not clearing, keep existing logo
        elif self.instance and self.instance.logo and not logo_clear:
            store.logo = self.instance.logo
            print(f"✅ Keeping existing logo: {store.logo}")

        if commit:
            store.save()
            print(f"✅ Store saved: {store.name} (ID: {store.id})")
        
        return store


# class MessageForm(forms.ModelForm):
#     class Meta:
#         model = Message
#         fields = ['receiver', 'content', 'subject']  # Including only fields you need for the form

#     receiver = forms.ModelChoiceField(queryset=CustomUser.objects.all())

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver', 'content']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Accept 'user' as an argument
        super().__init__(*args, **kwargs)

        if user:
            opposite_role = 'Admin' if user.role == 'User' else 'User'
            self.fields['receiver'].queryset = CustomUser.objects.filter(role=opposite_role, is_deleted=False)
        else:
            self.fields['receiver'].queryset = CustomUser.objects.none()  # Fallback if no user provided


class ImageUploadForm(forms.Form):
    image = forms.ImageField()

# class ImageUploadForm(forms.Form):
#     image = forms.ImageField()
#     model_type = forms.ChoiceField(choices=[('disease', 'Banana Disease Detection'), ('variety', 'Banana Variety Classification')])
