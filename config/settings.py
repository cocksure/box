from pathlib import Path
import environ
import os

env = environ.Env(
	DEBUG=(bool, False)
)
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, './.env'))
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG', default=False)

ALLOWED_HOSTS = ['boxproduction.vercel.app', 'boxproduction.pythonanywhere.com', '127.0.0.1']

INSTALLED_APPS = [
	'django.contrib.sites',
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',

	# packages
	'import_export',
	'rest_framework',
	'django_filters',
	'rest_framework.authtoken',
	'allauth',
	'allauth.account',
	'drf_yasg',
	'dj_rest_auth',
	'allauth.socialaccount',
	'corsheaders',
	'dj_rest_auth.registration',

	# local apps
	'apps.users',
	'apps.production',
	'apps.info',
	'apps.shared',
	'apps.depo',
	'apps.hr',
	'apps.api',

]

SWAGGER_SETTINGS = {
	'SECURITY_DEFINITIONS': {
		'basic': {
			'type': 'basic'
		}
	},
}

REST_FRAMEWORK = {
	'DEFAULT_PERMISSION_CLASSES': [
		'rest_framework.permissions.AllowAny',
	],

	'DEFAULT_AUTHENTICATION_CLASSES': [
		'rest_framework.authentication.SessionAuthentication',
		'rest_framework.authentication.TokenAuthentication',
	],
	'DEFAULT_FILTER_BACKENDS': [
		'django_filters.rest_framework.DjangoFilterBackend',
		'rest_framework.filters.SearchFilter',
		'rest_framework.filters.OrderingFilter',
	],
	'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.AutoSchema',

	'DEFAULT_PAGINATION_CLASS': 'apps.shared.utils.CustomPagination',
	'PAGE_SIZE': 20,

}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
	'http://localhost:3000',
	'http://localhost:8000',
	'http://0.0.0.0:8030',
	'https://boxproduction.pythonanywhere.com',
	'https://boxproduction.vercel.app'
]

AUTHENTICATION_BACKENDS = [
	'django.contrib.auth.backends.ModelBackend',
]
AUTH_USER_MODEL = 'users.CustomUser'

MIDDLEWARE = [
	'corsheaders.middleware.CorsMiddleware',
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.locale.LocaleMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'allauth.account.middleware.AccountMiddleware',

]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [BASE_DIR / 'templates']
		,
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

WSGI_APPLICATION = 'config.wsgi.application'

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": env('DB_NAME'),
#         "USER": env('DB_USER'),
#         "PASSWORD": env('DB_PASSWORD'),
#         "HOST": env('DB_HOST'),
#         "PORT": env('DB_PORT'),
#     }
# }

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': BASE_DIR / 'db.sqlite3',
	}
}

AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]

SITE_ID = 1

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
	BASE_DIR / 'static'
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

MEDIA_DIRS = [
	BASE_DIR / 'media_files',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'

# LOGGING = {
# 	'version': 1,
# 	'disable_existing_loggers': False,
# 	'handlers': {
# 		'console': {
# 			'level': 'DEBUG',
# 			'class': 'logging.StreamHandler',
# 		},
# 		'file': {
# 			'level': 'DEBUG',
# 			'class': 'logging.FileHandler',
# 			'filename': '/home/sanjar/PycharmProjects/box/logs.log',
# 		},
# 	},
# 	'loggers': {
# 		'django': {
# 			'handlers': ['console', 'file'],
# 			'level': 'DEBUG',
# 			'propagate': True,
# 		},
# 	},
# }
