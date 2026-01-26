from app.infrastructure.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password
from app.infrastructure.database.models import UserRole


class UserService:
    """Service class for handling user business logic."""
    
    def __init__(self, user_repository: UserRepository):
        """
        Initialize UserService with repository dependency.
        
        Args:
            user_repository: Repository for user data access
        """
        self.user_repository = user_repository
    
    async def create_user(self, user_data: UserCreate):
        """
        Create a new user with validation and password hashing.
        """
        # ... (las validaciones de email y username se quedan igual) ...
        # Check if email already exists
        existing_user_by_email = await self.user_repository.get_by_email(user_data.email)
        if existing_user_by_email:
            raise ValueError(f"Email {user_data.email} already exists")
        
        # Check if username already exists
        existing_user_by_username = await self.user_repository.get_by_username(user_data.username)
        if existing_user_by_username:
            raise ValueError(f"Username {user_data.username} already exists")
        
        # Hash the password
        hashed_password = get_password_hash(user_data.password)
        
        # CORRECCIÓN AQUÍ: Pasamos un DICCIONARIO en lugar de argumentos sueltos
        user_in_db = {
            "email": user_data.email,
            "username": user_data.username,
            "hashed_password": hashed_password,
            "full_name": user_data.full_name,
            "role": UserRole.CUSTOMER,  # Usamos el enum directamente
            "is_active": True
        }
        
        # El repositorio espera un solo argumento 'schema' (que puede ser dict)
        user = await self.user_repository.create(user_in_db)
        
        return user
    
    async def authenticate(self, email: str, password: str):
        """
        Authenticate a user by email and password.
        
        Args:
            email: User's email
            password: User's plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        # Get user by email
        user = await self.user_repository.get_by_email(email)
        if not user:
            return None
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            return None
        
        return user

