# /anvo/je;;yfish/utils/interactive_backend.property

# Moved from jelly_funcs.py to compartmentalize and stop auto-initializing interactivity when not needed (i.e. when now in full-featured app mode)



# Turns on/off interactivity (clicks and switches)

# def setup_matplotlib_backend():
#     """Smart matplotlib backend selection based on environment"""
#     import matplotlib
#     import sys
#     import os
    
#     # Check if we're in VS Code/Codium
#     is_vscode = any([
#         'VSCODE_PID' in os.environ,
#         'TERM_PROGRAM' in os.environ and 'vscode' in os.environ['TERM_PROGRAM'].lower(),
#         'code' in sys.argv[0].lower() if sys.argv else False
#     ])
    
#     # Check if we're running in Flask/web environment
#     is_flask = any([
#         'flask' in sys.modules,
#         'werkzeug' in sys.modules,
#         os.environ.get('FLASK_ENV'),
#         os.environ.get('WERKZEUG_RUN_MAIN'),
#         'gunicorn' in sys.argv[0] if sys.argv else False
#     ])
    
#     # Check if we're in a headless environment
#     is_headless = os.environ.get('DISPLAY') is None and os.name != 'nt'
    
#     if is_flask or is_headless:
#         matplotlib.use('Agg')
#         print("Using Agg backend (web/headless mode)")
#     elif is_vscode:
#         matplotlib.use('inline')  # or 'Agg' if you prefer
#         print("Using inline backend (VS Code mode)")

#     else:
#         # Interactive mode - try to use best available backend
#         try:
#             import platform
#             if platform.system() == 'Darwin':  # macOS
#                 try:
#                     matplotlib.use('macosx')
#                     print("🖥️  Using macOS backend (interactive mode)")
#                 except:
#                     matplotlib.use('TkAgg')
#                     print("🖥️  Using TkAgg backend (interactive mode)")
#             else:  # Windows/Linux
#                 matplotlib.use('TkAgg')
#                 print("🖥️  Using TkAgg backend (interactive mode)")
#         except Exception as e:
#             print(f"⚠️  Backend selection failed: {e}, falling back to Agg")
#             matplotlib.use('Agg')


# Alternate version

# def setup_matplotlib_backend(force_backend=None, verbose=True):
#     """
#     Smart matplotlib backend selection with comprehensive debugging
    
#     Args:
#         force_backend: If provided, force this backend (e.g., 'TkAgg', 'inline')
#         verbose: Print debug information
#     """
#     import matplotlib
#     import sys
#     import os
    
#     if verbose:
#         print("\n🎨 setup_matplotlib_backend() CALLED")
#         print(f"   Force backend: {force_backend}")
#         print(f"   Script: {sys.argv[0] if sys.argv else 'Unknown'}")
#         print(f"   Current backend: {matplotlib.get_backend()}")
    
#     # If force_backend is specified, use it immediately
#     if force_backend:
#         try:
#             matplotlib.use(force_backend, force=True)
#             if verbose:
#                 print(f"   ✅ FORCED backend to: {force_backend}")
#             return
#         except Exception as e:
#             if verbose:
#                 print(f"   ❌ Failed to force backend {force_backend}: {e}")
    
#     # Original detection logic with debugging
#     is_vscode = any([
#         'VSCODE_PID' in os.environ,
#         'TERM_PROGRAM' in os.environ and 'vscode' in os.environ['TERM_PROGRAM'].lower(),
#         len(sys.argv) > 0 and 'code' in sys.argv[0].lower()
#     ])
    
#     is_flask = any([
#         'flask' in sys.modules,
#         'werkzeug' in sys.modules,
#         os.environ.get('FLASK_ENV'),
#         os.environ.get('WERKZEUG_RUN_MAIN'),
#         len(sys.argv) > 0 and 'gunicorn' in sys.argv[0].lower()
#     ])
    
#     is_headless = os.environ.get('DISPLAY') is None and os.name != 'nt'
    
#     if verbose:
#         print(f"   Environment detection:")
#         print(f"     VS Code: {is_vscode}")
#         print(f"     Flask: {is_flask}") 
#         print(f"     Headless: {is_headless}")
    
#     if is_flask or is_headless:
#         matplotlib.use('Agg')
#         if verbose:
#             print("   ✅ Using Agg backend (web/headless mode)")
#     elif is_vscode:
#         matplotlib.use('inline')
#         if verbose:
#             print("   ✅ Using inline backend (VS Code mode)")
#     else:
#         # Interactive mode
#         try:
#             import platform
#             if platform.system() == 'Darwin':  # macOS
#                 try:
#                     matplotlib.use('macosx')
#                     if verbose:
#                         print("   ✅ Using macOS backend (interactive mode)")
#                 except:
#                     matplotlib.use('TkAgg')
#                     if verbose:
#                         print("   ✅ Using TkAgg backend (interactive mode)")
#             else:  # Windows/Linux
#                 matplotlib.use('TkAgg')
#                 if verbose:
#                     print("   ✅ Using TkAgg backend (interactive mode)")
#         except Exception as e:
#             if verbose:
#                 print(f"   ❌ Backend selection failed: {e}, falling back to Agg")
#             matplotlib.use('Agg')
    
#     if verbose:
#         print(f"   Final backend: {matplotlib.get_backend()}")
#         print("🎨 setup_matplotlib_backend() COMPLETED\n")
