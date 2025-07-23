from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
     model_config = SettingsConfigDict(env_file='.env')

     DATABASE_URI: str
     INPUT_FILE: str
     OUTPUT_FILE: str


settings = Settings()