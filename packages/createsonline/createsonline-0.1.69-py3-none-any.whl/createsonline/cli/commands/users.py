"""
CREATESONLINE User Management Commands

Create and manage users for the admin interface.
Lazy imports are used to avoid hard dependencies when not needed.
"""

import logging

_cli_logger = logging.getLogger("createsonline.cli.users")


def createsuperuser_command():
    """Create admin superuser interactively - works with or without rich/typer"""

    # Import dependencies only when command is used
    try:
        import typer
        from rich.console import Console
        from rich.prompt import Prompt, Confirm
        from rich.panel import Panel
        HAS_RICH = True
    except ImportError:
        HAS_RICH = False

    if HAS_RICH:
        # Use rich console for beautiful output
        console = Console()
        console.print(Panel(
            "[bold blue]CREATESONLINE Admin User Creation[/bold blue]\\n\\n"
            "[cyan]Create a superuser account for the admin interface.[/cyan]\\n"
            "[dim]This user will have full administrative privileges.[/dim]",
            title="Create Superuser",
            border_style="blue"
        ))
    else:
        # Fallback to simple print
        console = None
        print("\\n" + "="*60)
        print("CREATESONLINE Admin User Creation")
        print("="*60)
        print("Create a superuser account for the admin interface.")
        print("This user will have full administrative privileges.")
        print("="*60 + "\\n")

    # Get user information
    try:
        if HAS_RICH:
            username = Prompt.ask("[cyan]Username[/cyan]", default="admin")
            email = Prompt.ask("[cyan]Email address[/cyan]", default=f"{username}@example.com")
            password = Prompt.ask("[cyan]Password[/cyan]", password=True)
            password_confirm = Prompt.ask("[cyan]Confirm password[/cyan]", password=True)
        else:
            # Fallback to standard input
            import getpass
            username = input("Username [admin]: ").strip() or "admin"
            email = input(f"Email address [{username}@example.com]: ").strip() or f"{username}@example.com"
            password = getpass.getpass("Password: ")
            password_confirm = getpass.getpass("Confirm password: ")

        if password != password_confirm:
            if HAS_RICH:
                console.print("[red]Passwords don't match![/red]")
                raise typer.Exit(1)
            else:
                print("ERROR: Passwords don't match!")
                return

        # Confirm creation
        if HAS_RICH:
            console.print(f"\\n[green]Creating superuser:[/green]")
            console.print(f"  Username: [cyan]{username}[/cyan]")
            console.print(f"  Email: [cyan]{email}[/cyan]")
            if not Confirm.ask("\\n[yellow]Create this superuser?[/yellow]"):
                console.print("[yellow]Cancelled[/yellow]")
                return
        else:
            print(f"\\nCreating superuser:")
            print(f"  Username: {username}")
            print(f"  Email: {email}")
            confirm = input("\\nCreate this superuser? [Y/n]: ").strip().lower()
            if confirm and confirm not in ['y', 'yes']:
                print("Cancelled")
                return

        # Create the user
        success = create_superuser(username, email, password, console)

        if success:
            if HAS_RICH:
                console.print(Panel(
                    f"[bold green]Success! Superuser '{username}' created successfully![/bold green]\\n\\n"
                    "[cyan]You can now:[/cyan]\\n"
                    "- Login to admin interface\\n"
                    "- Manage users and permissions\\n"
                    "- Configure application settings\\n\\n"
                    "[green]Admin URL:[/green] http://localhost:8000/admin/",
                    title="Success!",
                    border_style="green"
                ))
            else:
                print("\\n" + "="*60)
                print(f"SUCCESS: Superuser '{username}' created successfully!")
                print("="*60)
                print("\\nYou can now:")
                print("  - Login to admin interface")
                print("  - Manage users and permissions")
                print("  - Configure application settings")
                print("\\nAdmin URL: http://localhost:8000/admin/")
                print("="*60 + "\\n")
        else:
            if HAS_RICH:
                console.print("[red]Failed to create superuser[/red]")
                raise typer.Exit(1)
            else:
                print("ERROR: Failed to create superuser")

    except KeyboardInterrupt:
        if HAS_RICH:
            console.print("\\n[yellow]Cancelled by user[/yellow]")
        else:
            print("\\nCancelled by user")
    except Exception as e:
        if HAS_RICH:
            console.print(f"[red]Error creating superuser: {e}[/red]")
            raise typer.Exit(1)
        else:
            print(f"ERROR: Error creating superuser: {e}")
            import traceback
            traceback.print_exc()


def create_superuser(username: str, email: str, password: str, console=None) -> bool:
    """Create a superuser in the database.

    Returns True on success, False otherwise. Accepts optional `console`
    for rich output; falls back to print when not provided.
    """

    try:
        # Try to import models from the current project first
        import sys
        import os
        import hashlib
        from pathlib import Path
        from urllib.parse import quote_plus
        from dotenv import load_dotenv

        # Load .env file if it exists
        env_path = Path('.env')
        if env_path.exists():
            load_dotenv(env_path)

        # Add current directory to path to import project models
        sys.path.insert(0, os.getcwd())

        # Initialize database first (for Createsonline 0.1.67+)
        try:
            from createsonline.database import init_db
            from user_config import DATABASE_URL
            init_db(DATABASE_URL, create_tables=False)
        except:
            pass

        # Try to import User model and UserRole
        try:
            # Try apps structure first (meahmedh style)
            from apps.cms.auth_models import User as UserModel, UserRole
            has_user_role = True
            model_name = "User"
        except ImportError:
            try:
                # Try models.py in current directory
                from models import User as UserModel
                has_user_role = hasattr(UserModel, '__table__') and 'role' in [c.name for c in UserModel.__table__.columns]
                if has_user_role:
                    try:
                        from models import UserRole
                    except:
                        has_user_role = False
                model_name = "User"
            except ImportError:
                try:
                    # Try framework User model
                    from createsonline.auth.models import User as UserModel
                    has_user_role = False
                    model_name = "User"
                except ImportError:
                    _cli_logger.error("No User model found. Create a User model in your project.")
                    return False

        # Get database session
        try:
            from createsonline.database import get_database
            db = get_database()
            session = db.get_session()
        except:
            # Fallback to manual session creation
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            from user_config import DATABASE_URL
            engine = create_engine(DATABASE_URL)
            SessionLocal = sessionmaker(bind=engine)
            session = SessionLocal()

        try:
            # Check if user already exists
            existing_user = session.query(UserModel).filter(UserModel.username == username).first()
            if existing_user:
                msg = f"{model_name} '{username}' already exists!"
                (console.print(f"[yellow]{msg}[/yellow]") if console else print(msg))
                return False

            # Hash password
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            # Create the user with appropriate role
            user_kwargs = dict(
                username=username,
                email=email,
                password_hash=password_hash,
                is_active=True,
                is_verified=True
            )

            # Add role if the model supports it
            if has_user_role:
                user_kwargs['role'] = UserRole.SYSTEM_ADMIN
            else:
                # Fallback to is_superuser for framework User
                user_kwargs['is_superuser'] = True

            user = UserModel(**user_kwargs)
            session.add(user)
            session.commit()

            msg = f"{model_name} '{username}' created successfully!"
            (console.print(f"[green]{msg}[/green]") if console else print(msg))
            return True

        finally:
            session.close()

    except Exception as e:
        _cli_logger.error(f"Error creating superuser: {e}")
        import traceback
        traceback.print_exc()
        return False



