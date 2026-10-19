#!/usr/bin/env python3
"""Wrapper: trace PNG -> SVG via vtracer (run inside the microstock .venv)."""
import sys, vtracer

def main():
    if len(sys.argv) < 3:
        print("usage: vectorize.py <in.png> <out.svg>")
        sys.exit(2)
    src, dst = sys.argv[1], sys.argv[2]
    vtracer.convert_image_to_svg_py(
        src, dst,
        colormode='color',
        filter_speckle=4,
        color_precision=6,
        layer_difference=16,
        mode='spline',
        corner_threshold=60,
        length_threshold=4.0,
        max_iterations=10,
        splice_threshold=45,
        path_precision=3,
    )
    print("OK", dst)

if __name__ == '__main__':
    main()