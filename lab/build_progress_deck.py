"""Build an editable, dependency-free PPTX plus SVG/PNG previews from project evidence.
Historical presentation snapshot; current scientific guidance remains in repository markdown.
"""
from pathlib import Path
from xml.sax.saxutils import escape
import zipfile,json,textwrap,ctypes,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'lab/v';EMU=914400
NAVY='142B43';BLUE='0072B2';ORANGE='D55E00';GRAY='5B6572';LIGHT='EAF1F6';WHITE='FFFFFF'
NS='http://schemas.openxmlformats.org';A=NS+'/drawingml/2006/main';P=NS+'/presentationml/2006/main';R=NS+'/officeDocument/2006/relationships'
class Extents(ctypes.Structure):
 _fields_=[(k,ctypes.c_double) for k in ('xb','yb','w','h','xa','ya')]
CAIRO=ctypes.CDLL('libcairo.so.2')
CAIRO.cairo_image_surface_create.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int];CAIRO.cairo_image_surface_create.restype=ctypes.c_void_p
CAIRO.cairo_create.argtypes=[ctypes.c_void_p];CAIRO.cairo_create.restype=ctypes.c_void_p
CAIRO.cairo_select_font_face.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_int,ctypes.c_int]
CAIRO.cairo_set_font_size.argtypes=[ctypes.c_void_p,ctypes.c_double]
CAIRO.cairo_text_extents.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.POINTER(Extents)]
MEASURE=CAIRO.cairo_create(CAIRO.cairo_image_surface_create(0,1,1))
def wrapped(text,width,size,bold):
 CAIRO.cairo_select_font_face(MEASURE,b'Arial',0,int(bold));CAIRO.cairo_set_font_size(MEASURE,size)
 result=[];line=''
 for word in text.split():
  test=(line+' '+word).strip();ex=Extents();CAIRO.cairo_text_extents(MEASURE,test.encode(),ctypes.byref(ex))
  if ex.xa>width*72-3 and line:result.append(line);line=word
  else:line=test
 return result+[line]
def e(v):return escape(str(v))
class Slide:
 def __init__(self,title,source):
  self.items=[];self.source=source;self.title=title
  self.rect(0,0,13.333,.16,NAVY);self.text(.6,.4,12.1,.7,title,29,NAVY,bold=True)
 def rect(self,x,y,w,h,color,ellipse=False):self.items.append(dict(kind='shape',x=x,y=y,w=w,h=h,color=color,ellipse=ellipse))
 def text(self,x,y,w,h,text,size=22,color=NAVY,bold=False):
  # Explicit line wrapping is shared with previews; keep generous margins.
  lines=[]
  for p in text.split('\n'):
   lines+=wrapped(p,w,size,bold)
  assert len(lines)*size*1.24/72<=h+.12,(self.title,text,len(lines),h)
  self.items.append(dict(kind='text',x=x,y=y,w=w,h=h,lines=lines,size=size,color=color,bold=bold))
 def bullet(self,y,heading,body):
  self.rect(.65,y+.1,.12,.12,BLUE);self.text(.95,y,11.7,.45,heading,23,bold=True);self.text(.95,y+.5,11.6,.9,body,20,GRAY)
 def finish(self,i,n):
  self.rect(.6,6.93,12.1,.012,'CDD6DF');self.text(.6,7.03,11.4,.25,self.source,10,GRAY);self.text(12,7.02,.8,.3,f'{i}/{n}',11,GRAY)
 def xml(self):
  shapes=[]
  for i,v in enumerate(self.items,2):
   x,y,w,h=[round(v[k]*EMU) for k in ('x','y','w','h')]
   xf=f'<a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
   if v['kind']=='shape':
    body=f'<p:spPr>{xf}<a:prstGeom prst="{"ellipse" if v["ellipse"] else "rect"}"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{v["color"]}"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr>'
   else:
    ps=[]
    for line in v['lines']:
     ps.append(f'<a:p><a:pPr><a:lnSpc><a:spcPct val="124000"/></a:lnSpc></a:pPr><a:r><a:rPr lang="en-GB" sz="{v["size"]*100}" b="{int(v["bold"])}"><a:solidFill><a:srgbClr val="{v["color"]}"/></a:solidFill><a:latin typeface="Arial"/></a:rPr><a:t>{e(line)}</a:t></a:r><a:endParaRPr lang="en-GB" sz="{v["size"]*100}"/></a:p>')
    body=f'<p:spPr>{xf}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"/><a:lstStyle/>{"".join(ps)}</p:txBody>'
   shapes.append(f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="Shape {i}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>{body}</p:sp>')
  return f'<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree>{group()}{"".join(shapes)}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
 def svg(self):
  z=['<svg xmlns="http://www.w3.org/2000/svg" width="1333" height="750" viewBox="0 0 1333 750"><rect width="1333" height="750" fill="white"/>']
  for v in self.items:
   x,y,w,h=[v[k]*100 for k in ('x','y','w','h')]
   if v['kind']=='shape':
    z.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#{v["color"]}" rx="{w/2 if v["ellipse"] else 0}"/>')
   else:
    fs=v['size']*100/72
    for k,line in enumerate(v['lines']):z.append(f'<text x="{x}" y="{y+fs*(.92+1.24*k)}" font-family="Arial,sans-serif" font-size="{fs}" font-weight="{"bold" if v["bold"] else "normal"}" fill="#{v["color"]}">{e(line)}</text>')
  return ''.join(z)+'</svg>'
def group():return '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
def rels(items):return '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(f'<Relationship Id="{id}" Type="{R}/{typ}" Target="{target}"/>' for id,typ,target in items)+'</Relationships>'
def build():
 slides=[]
 def new(t,src):s=Slide(t,src);slides.append(s);return s
 s=new('The original goal: intelligence that scales','Research review • 18 November 2026 • README: The goal')
 s.text(.8,1.6,11.7,1.45,'“To solve a bigger problem, just add more brain.”',36,BLUE,bold=True)
 s.text(.8,3.35,11.6,1.4,'One reusable design that learns and reorganises during life, without us inventing a new solution for each unfamiliar problem.',25)
 s.text(.8,5.3,11.7,.8,'Progress: useful capabilities and sharper explanations. General, economical scaling is still unproved.',22,GRAY)
 s=new('What would count as success?','Sources: README goal and scaling test; GRAMMAR evaluation protocol')
 s.bullet(1.5,'Learn in life','Approach a strong, explicitly informed reference on unfamiliar challenges.')
 s.bullet(3.15,'Scale with a frozen design','Additional resources extend capability across families and retain simpler skills.')
 s.bullet(4.8,'Pay the full cost','Evidence, learning time, material, energy and communication all count. Locality must survive growth.')
 s=new('A small robot makes the problem observable','Sources: AGENTS ground rules; README; GRAMMAR')
 for x,label in [(1,'World'),(4.55,'Brain'),(8.1,'Action')]:
  s.rect(x,2,2.7,1.3,LIGHT);s.text(x+.18,2.35,2.34,.6,label,27,BLUE,bold=True)
 s.text(3.77,2.4,.6,.5,'→',28);s.text(7.32,2.4,.6,.5,'→',28)
 s.text(.9,3.7,11.5,1.1,'Two sensors, two motors, one food/poison taste. Wiring varies each life. Actions change the evidence the brain receives.',23)
 s.text(.9,5.25,11.5,.9,'Challenges include sequences, timing and combinations. Same seed helps pair lives; it does not make their observations identical.',21,GRAY)
 s=new('Progress: three useful pieces, not the whole goal','Sources: minimal/NOTEBOOK; discrete D65–D72; ABSTRACT')
 s.bullet(1.45,'Compact circuits learn a basic food distinction','A working foundation; later physical accounting changed the apparent size and cost.')
 s.bullet(3.1,'Timing improved after a causal diagnosis','Separating cycle position, trust recovery and period estimation led to better tracking.')
 s.bullet(4.75,'More capacity helps sequence challenges','Timing scales less regularly; combined challenges and reuse remain difficult.')
 s=new('The most durable discoveries','Sources: discrete D44–D54, D73–D82; README findings')
 s.bullet(1.45,'Information has to reach useful action','Predictability alone can reward unhelpful behaviour. Movement changes what can be learned.')
 s.bullet(3.1,'Score the prediction that was actually issued','Learning and recycling can change a speaker before credit arrives. Correct timing matters.')
 s.bullet(4.75,'A capacity setting is not a material bill','Fixed machinery, actual occupancy, activity and global scans need separate accounts.')
 s=new('Why we investigated memory allocation','Sources: discrete D76–D78, D93–D108')
 s.text(.85,1.5,11.6,1.15,'Extra memory is valuable in some streams, but the allocator often sends it elsewhere.',27,BLUE,bold=True)
 s.bullet(3.0,'A hand-informed allocation is a useful reference','It recovers much of the larger brain’s sequence performance, but supplies knowledge the brain must discover.')
 s.bullet(4.7,'Retention and weighting have not supplied a general cure','Reappearing memories are not automatically useful. Hindsight winners and small replay effects are not causal proofs.')
 s=new('The recent test changed one admission rule','Sources: discrete D109–D118; spare_allowance.py')
 s.text(.85,1.5,11.6,1,'Old rule: a donor must delete a unit to transfer allowance—even if it has spare allowance and no unit to delete.',25)
 s.text(.85,3.05,11.6,1,'Tested change: allow that spare allowance to move without deletion. Keep the price, donor draw and credit contract fixed.',25,BLUE)
 s.text(.85,4.65,11.6,1.25,'Both arms: cap 2300 units; sequence and timing challenges; ten opened seed pairs. All-food controls match exactly. This remains a software diagnostic with global scans.',21,GRAY)
 s=new('Efficiency gains remain inconclusive','Source: D117; independently reproduced in D120. Bootstrap 95% intervals; development data.')
 s.text(.85,1.4,11.6,.65,'Change in fraction of the circuit-to-told performance gap closed',20,GRAY)
 lo,hi=-.12,.25;x0,x1=4.0,11.7
 def xx(v):return x0+(v-lo)/(hi-lo)*(x1-x0)
 s.rect(xx(0),2.25,.016,2.8,'AAB4BF')
 for label,y,val,l,h,col,ell in [('Sequence',2.8,.046919,-.012947,.107937,BLUE,True),('Timing',4.1,.109028,-.017631,.211134,ORANGE,False)]:
  s.text(.9,y-.15,2.7,.5,label,24,bold=True);s.rect(xx(l),y,xx(h)-xx(l),.035,col)
  for end in (l,h):s.rect(xx(end),y-.12,.02,.27,col)
  s.rect(xx(val)-.075,y-.06,.15,.15,col,ell)
  s.text(4,y+.35,7.7,.5,f'{val:+.3f}  [{l:+.3f}, {h:+.3f}]',19,col)
 s.text(.9,5.7,11.5,.8,'Both intervals cross zero. Neither establishes improvement; neither establishes equality. No larger run follows automatically.',21)
 s=new('Latest test: contribution to prediction','Sources: K/L, discrete D121–D122; gate_contribution_capture.json')
 result=OUT/'gate_contribution_capture.json'
 if result.exists():
  d=json.loads(result.read_text());g=[r for r in d['lives'] if r['arm']=='issued+gate']
  s.text(.85,1.45,11.6,.9,'Eight exact passive replays; one seed pair per family.',25,BLUE,bold=True)
  y=2.65
  for c,label in [('seq','Sequence'),('time','Timing')]:
   rr=[r for r in g if r['cond']==c];vals=[r['windows']['same_call full']['bits_total'] for r in rr]
   s.text(.9,y,11.4,.65,f'{label}: full-life contribution {vals[0]:+.3f} / {vals[1]:+.3f} bits (red / blue)',22);y+=.8
  s.text(.9,4.65,11.4,1.3,'Measured by replacing the selected forecasts with the default while keeping weights and observations fixed. Positive means helpful on that history—not a causal foraging effect.',21,GRAY)
 else:
  s.bullet(1.6,'Standalone bit totals were the wrong measure','They can cancel while the weighted mixture benefits. They do not bound contribution.')
  s.bullet(3.4,'Capture actual issued weights and forecasts','Eight existing lives; no controller change. Results pending at build time.')
 s=new('What the recent work settles','Sources: D120–D122; PROGRAMME')
 s.bullet(1.45,'Settled: the spare-allowance obstruction is real','The gate can move usable room without violating the cap or changing all-food behaviour.')
 s.bullet(3.1,'Unsettled: why performance changes','Forecast contribution, preserved ancestry and changed future observations are different routes.')
 s.bullet(4.75,'Unsettled: the economical local implementation','The allocator scans globally; the diagnostic wrapper adds work. CPU time is not a silicon power estimate.')
 s=new('Step back: how close are we to the original goal?','Sources: README goal; discrete evidence review D72; current programme')
 rows=[('In-life adaptation','Demonstrated in specific tasks'),('Reusable components','Useful components; design still contains supplied structure'),('General scaling','Not established across unfamiliar families'),('Economical growth','Resource and communication account incomplete')]
 for i,(a,b) in enumerate(rows):
  y=1.55+i*1.15;s.rect(.8,y,11.75,.95,LIGHT if i%2==0 else 'F5F7F9');s.text(1,y+.18,3.5,.65,a,21,bold=True);s.text(4.65,y+.18,7.5,.65,b,20)
 s=new('Next steps: explanation before expansion','Research recommendations, not permission to open protected tests or launch a sweep')
 s.bullet(1.45,'Choose the causal question worth answering','Use the new measurements to decide between direct forecasts, preservation and changed observations. Freeze one test.')
 s.bullet(3.1,'Reconnect the result to general scaling','Retain only capabilities with a clear purpose, evidence and cost. Compare tuning, recycling and growth fairly.')
 s.bullet(4.75,'Validate only after an exploratory benefit is credible','Then use fresh seeds, step refinement and declared practical margins. Keep genuinely new families protected.')
 s=new('Evidence map and reading guide','Snapshot generated from the local repository; the markdown remains the current source of truth')
 sources=[('Goal and success criteria','README.md; GRAMMAR.md'),('Research position and open questions','ABSTRACT.md; QUESTIONS.md; PROGRAMME.md'),('Foundations and scaling review','minimal/NOTEBOOK.md; discrete/NOTEBOOK.md D65–D78'),('Credit, retention and allocation','discrete/NOTEBOOK.md D79–D112'),('Gate comparison and its limitations','discrete/NOTEBOOK.md D113–D120'),('Latest attribution and contribution tests','discrete/NOTEBOOK.md D121–D122; lab/v/gate_contribution_capture.json')]
 for i,(a,b) in enumerate(sources):s.text(.85,1.35+i*.8,11.6,.32,a,18,bold=True);s.text(.85,1.69+i*.8,11.6,.35,b,14,GRAY)
 for i,s in enumerate(slides,1):s.finish(i,len(slides))
 return slides

def package(slides):
 files={};add=lambda k,v:files.__setitem__(k,v)
 add('_rels/.rels',rels([('rId1','officeDocument','ppt/presentation.xml')]))
 add('ppt/presentation.xml',f'<p:presentation xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst>'+''.join(f'<p:sldId id="{256+i}" r:id="rId{i+2}"/>' for i in range(len(slides)))+'</p:sldIdLst><p:sldSz cx="12192000" cy="6858000" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>')
 add('ppt/_rels/presentation.xml.rels',rels([('rId1','slideMaster','slideMasters/slideMaster1.xml')]+[(f'rId{i+2}','slide',f'slides/slide{i+1}.xml') for i in range(len(slides))]))
 colors='<a:dk1><a:srgbClr val="000000"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="142B43"/></a:dk2><a:lt2><a:srgbClr val="EAF1F6"/></a:lt2>'+''.join(f'<a:accent{i}><a:srgbClr val="{c}"/></a:accent{i}>' for i,c in enumerate([BLUE,ORANGE,'009E73','CC79A7','56B4E9','F0E442'],1))+'<a:hlink><a:srgbClr val="0072B2"/></a:hlink><a:folHlink><a:srgbClr val="CC79A7"/></a:folHlink>'
 fill='<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
 theme=f'<a:theme xmlns:a="{A}" name="Simple Learner"><a:themeElements><a:clrScheme name="Accessible">{colors}</a:clrScheme><a:fontScheme name="Arial"><a:majorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="Simple"><a:fillStyleLst>{fill*3}</a:fillStyleLst><a:lnStyleLst>'+''.join(f'<a:ln w="{w}">{fill}<a:prstDash val="solid"/><a:miter lim="800000"/></a:ln>' for w in [9525,25400,38100])+f'</a:lnStyleLst><a:effectStyleLst>{"<a:effectStyle><a:effectLst/></a:effectStyle>"*3}</a:effectStyleLst><a:bgFillStyleLst>{fill*3}</a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>'
 add('ppt/theme/theme1.xml',theme)
 cmap='<p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/>'
 add('ppt/slideMasters/slideMaster1.xml',f'<p:sldMaster xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:cSld><p:spTree>{group()}</p:spTree></p:cSld>{cmap}<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>')
 add('ppt/slideMasters/_rels/slideMaster1.xml.rels',rels([('rId1','slideLayout','../slideLayouts/slideLayout1.xml'),('rId2','theme','../theme/theme1.xml')]))
 add('ppt/slideLayouts/slideLayout1.xml',f'<p:sldLayout xmlns:p="{P}" xmlns:a="{A}" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree>{group()}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>')
 add('ppt/slideLayouts/_rels/slideLayout1.xml.rels',rels([('rId1','slideMaster','../slideMasters/slideMaster1.xml')]))
 for i,s in enumerate(slides,1):
  add(f'ppt/slides/slide{i}.xml',s.xml());add(f'ppt/slides/_rels/slide{i}.xml.rels',rels([('rId1','slideLayout','../slideLayouts/slideLayout1.xml')]))
 types={'ppt/presentation.xml':'presentation.main','ppt/slideMasters/slideMaster1.xml':'slideMaster','ppt/slideLayouts/slideLayout1.xml':'slideLayout',**{f'ppt/slides/slide{i}.xml':'slide' for i in range(1,len(slides)+1)}}
 add('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'+''.join(f'<Override PartName="/{k}" ContentType="application/vnd.openxmlformats-officedocument.presentationml.{v}+xml"/>' for k,v in types.items())+'<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/></Types>')
 for xml in files.values():ET.fromstring(xml)
 path=OUT/'simple_learner_progress_review.pptx'
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  for k,v in files.items():z.writestr(k,'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'+v)
 return path

def render(svgpath,pngpath):
 r=ctypes.CDLL('librsvg-2.so.2');c=ctypes.CDLL('libcairo.so.2');g=ctypes.CDLL('libgobject-2.0.so.0')
 r.rsvg_handle_new_from_file.argtypes=[ctypes.c_char_p,ctypes.c_void_p];r.rsvg_handle_new_from_file.restype=ctypes.c_void_p
 r.rsvg_handle_render_cairo.argtypes=[ctypes.c_void_p,ctypes.c_void_p];r.rsvg_handle_render_cairo.restype=ctypes.c_int
 c.cairo_image_surface_create.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int];c.cairo_image_surface_create.restype=ctypes.c_void_p
 c.cairo_create.argtypes=[ctypes.c_void_p];c.cairo_create.restype=ctypes.c_void_p
 c.cairo_surface_write_to_png.argtypes=[ctypes.c_void_p,ctypes.c_char_p];c.cairo_surface_write_to_png.restype=ctypes.c_int
 c.cairo_destroy.argtypes=[ctypes.c_void_p];c.cairo_surface_destroy.argtypes=[ctypes.c_void_p];g.g_object_unref.argtypes=[ctypes.c_void_p]
 h=r.rsvg_handle_new_from_file(str(svgpath).encode(),None);assert h
 surface=c.cairo_image_surface_create(0,1333,750);cr=c.cairo_create(surface);assert r.rsvg_handle_render_cairo(h,cr)
 assert c.cairo_surface_write_to_png(surface,str(pngpath).encode())==0
 c.cairo_destroy(cr);c.cairo_surface_destroy(surface);g.g_object_unref(h)
if __name__=='__main__':
 slides=build();path=package(slides);preview=OUT/'progress_deck_preview';preview.mkdir(exist_ok=True)
 for i,s in enumerate(slides,1):
  svg=preview/f'slide_{i:02d}.svg';svg.write_text(s.svg());render(svg,svg.with_suffix('.png'))
 (OUT/'simple_learner_progress_review_outline.md').write_text('# Presentation snapshot — 18 November 2026\n\n'+ '\n\n'.join(f'## {i}. {s.title}\n\n'+ '\n'.join(' '.join(v['lines']) for v in s.items if v['kind']=='text') for i,s in enumerate(slides,1)))
 print(path, len(slides),'slides; XML parsed; SVG previews rendered. These previews use the same content/geometry, not an Office renderer.')
