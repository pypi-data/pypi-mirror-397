"""ASCII Logo generator for HOS SecSuite"""

import time


class ASCIITypes:
    """ASCII Logo types"""
    STATIC = "static"
    ANIMATED = "animated"
    SIMPLE = "simple"


def generate_logo(variant: str = ASCIITypes.STATIC) -> str:
    """Generate ASCII logo with ANSI colors
    
    Args:
        variant: Logo variant (static, animated, simple)
        
    Returns:
        str: Generated ASCII logo
    """
    if variant == ASCIITypes.ANIMATED:
        return _generate_animated_logo()
    elif variant == ASCIITypes.SIMPLE:
        return _generate_simple_logo()
    else:
        return _generate_static_logo()


def _generate_static_logo() -> str:
    """Generate static ASCII logo"""
    logo = """
\033[95m╔══════════════════════════════════════════════════════════╗\033[0m
\033[95m║\033[31m  ██╗  ██╗ ██████╗ ███████╗ ██████╗ ██╗   ██╗███████╗     \033[95m║\033[0m
\033[95m║\033[31m  ██║  ██║██╔═══██╗██╔════╝██╔═══██╗██║   ██║██╔════╝     \033[95m║\033[0m
\033[95m║\033[31m  ███████║██║   ██║█████╗  ██║   ██║██║   ██║█████╗       \033[95m║\033[0m
\033[95m║\033[31m  ██╔══██║██║   ██║██╔══╝  ██║   ██║██║   ██║██╔══╝       \033[95m║\033[0m
\033[95m║\033[31m  ██║  ██║╚██████╔╝██║     ╚██████╔╝╚██████╔╝███████╗     \033[95m║\033[0m
\033[95m║\033[31m  ╚═╝  ╚═╝ ╚═════╝ ╚═╝      ╚═════╝  ╚═════╝ ╚══════╝     \033[95m║\033[0m
\033[95m║\033[32m                     HOS-SecSuite v0.1.1                    \033[95m║\033[0m
\033[95m║\033[32m       Modular Network Security Toolkit - Defense First    \033[95m║\033[0m
\033[95m╚══════════════════════════════════════════════════════════╝\033[0m
    """
    return logo


def _generate_simple_logo() -> str:
    """Generate simple ASCII logo"""
    logo = """
\033[31m  ██╗  ██╗ ██████╗ ███████╗
\033[31m  ██║  ██║██╔═══██╗██╔════╝
\033[31m  ███████║██║   ██║█████╗
\033[31m  ██╔══██║██║   ██║██╔══╝
\033[31m  ██║  ██║╚██████╔╝██║
\033[31m  ╚═╝  ╚═╝ ╚═════╝ ╚═╝
\033[32m  HOS-SecSuite v0.1.1
\033[32m  Modular Network Security Toolkit
    """
    return logo


def _generate_animated_logo() -> str:
    """Generate animated ASCII logo"""
    # For animated logo, we'll return a sequence of frames
    # In the console, we'll print them sequentially
    frames = []
    
    # Frame 1: Simple outline
    frame1 = """
┌─────────────────────────────────────────┐
│                                         │
│          HOS-SecSuite v0.1.1            │
│     Modular Network Security Toolkit    │
│                                         │
└─────────────────────────────────────────┘
    """
    frames.append(frame1)
    
    # Frame 2: Add color
    frame2 = """
\033[95m┌─────────────────────────────────────────┐\033[0m
\033[95m│                                         │\033[0m
\033[95m│\033[31m          HOS-SecSuite v0.1.1            \033[95m│\033[0m
\033[95m│\033[32m     Modular Network Security Toolkit    \033[95m│\033[0m
\033[95m│                                         │\033[95m│\033[0m
\033[95m└─────────────────────────────────────────┘\033[0m
    """
    frames.append(frame2)
    
    # Frame 3: Complete logo
    frame3 = _generate_static_logo()
    frames.append(frame3)
    
    # Join frames with delay markers
    return "\n---FRAME---\n".join(frames)


def print_logo(variant: str = ASCIITypes.STATIC) -> None:
    """Print ASCII logo to console
    
    Args:
        variant: Logo variant
    """
    if variant == ASCIITypes.ANIMATED:
        # Print animated frames sequentially
        frames = generate_logo(variant).split("\n---FRAME---\n")
        for frame in frames:
            print("\033[H\033[J", end="")  # Clear screen
            print(frame)
            time.sleep(0.5)
    else:
        print(generate_logo(variant))
