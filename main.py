"""
Root entry point redirecting to vfd_hmi/main.py.
Allows running 'python main.py' directly from the root workspace directory.
"""
import os
import sys

if __name__ == "__main__":
    vfd_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vfd_hmi")
    sys.path.insert(0, vfd_dir)
    os.chdir(vfd_dir)
    
    from main import main
    main()
