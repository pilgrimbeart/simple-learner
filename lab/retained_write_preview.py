"""Render our SVG artifacts with pygame; add SVG text omitted by SDL_image's SVG loader."""
import os,sys,xml.etree.ElementTree as ET
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
import pygame
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'lab/v/retained_write'

def render(path):
    pygame.font.init();surface=pygame.image.load(str(path));tree=ET.parse(path)
    for node in tree.iter():
        if node.tag.endswith('}text'):
            size=int(node.attrib.get('font-size',14));font=pygame.font.SysFont('sans',size)
            text=''.join(node.itertext());x=float(node.attrib.get('x',0));y=float(node.attrib.get('y',0))
            color=node.attrib.get('fill','#222222')
            if color.startswith('#') and len(color)==4:color='#'+''.join(c*2 for c in color[1:])
            surface.blit(font.render(text,True,color),(x,y-font.get_ascent()))
    pygame.image.save(surface,str(path.with_suffix('.png')));return surface

if __name__=='__main__':
    stage=sys.argv[1] if len(sys.argv)>1 else 'confirm';panels=[render(OUT/f'{stage}_panel_{i}.svg') for i in range(4)]
    surface=pygame.Surface((1080,580));surface.fill('white')
    for i,panel in enumerate(panels):surface.blit(panel,((i%2)*540,(i//2)*290))
    pygame.image.save(surface,str(OUT/f'{stage}_overview.png'));render(OUT/'schematic_v1.svg')
