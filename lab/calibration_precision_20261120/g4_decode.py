"""Minimal CCITT Group 4 (T.6) decoder for scanned PDF pages -> grayscale PNG (2x downsampled). Reads only data."""
import re,sys,zlib,struct
WT="""0 00110101|1 000111|2 0111|3 1000|4 1011|5 1100|6 1110|7 1111|8 10011|9 10100|10 00111|11 01000|12 001000|13 000011|14 110100|15 110101|16 101010|17 101011|18 0100111|19 0001100|20 0001000|21 0010111|22 0000011|23 0000100|24 0101000|25 0101011|26 0010011|27 0100100|28 0011000|29 00000010|30 00000011|31 00011010|32 00011011|33 00010010|34 00010011|35 00010100|36 00010101|37 00010110|38 00010111|39 00101000|40 00101001|41 00101010|42 00101011|43 00101100|44 00101101|45 00000100|46 00000101|47 00001010|48 00001011|49 01010010|50 01010011|51 01010100|52 01010101|53 00100100|54 00100101|55 01011000|56 01011001|57 01011010|58 01011011|59 01001010|60 01001011|61 00110010|62 00110011|63 00110100|64 11011|128 10010|192 010111|256 0110111|320 00110110|384 00110111|448 01100100|512 01100101|576 01101000|640 01100111|704 011001100|768 011001101|832 011010010|896 011010011|960 011010100|1024 011010101|1088 011010110|1152 011010111|1216 011011000|1280 011011001|1344 011011010|1408 011011011|1472 010011000|1536 010011001|1600 010011010|1664 011000|1728 010011011"""
BT="""0 0000110111|1 010|2 11|3 10|4 011|5 0011|6 0010|7 00011|8 000101|9 000100|10 0000100|11 0000101|12 0000111|13 00000100|14 00000111|15 000011000|16 0000010111|17 0000011000|18 0000001000|19 00001100111|20 00001101000|21 00001101100|22 00000110111|23 00000101000|24 00000010111|25 00000011000|26 000011001010|27 000011001011|28 000011001100|29 000011001101|30 000001101000|31 000001101001|32 000001101010|33 000001101011|34 000011010010|35 000011010011|36 000011010100|37 000011010101|38 000011010110|39 000011010111|40 000001101100|41 000001101101|42 000011011010|43 000011011011|44 000001010100|45 000001010101|46 000001010110|47 000001010111|48 000001100100|49 000001100101|50 000001010010|51 000001010011|52 000000100100|53 000000110111|54 000000111000|55 000000100111|56 000000101000|57 000001011000|58 000001011001|59 000000101011|60 000000101100|61 000001011010|62 000001100110|63 000001100111|64 0000001111|128 000011001000|192 000011001001|256 000001011011|320 000000110011|384 000000110100|448 000000110101|512 0000001101100|576 0000001101101|640 0000001001010|704 0000001001011|768 0000001001100|832 0000001001101|896 0000001110010|960 0000001110011|1024 0000001110100|1088 0000001110101|1152 0000001110110|1216 0000001110111|1280 0000001010010|1344 0000001010011|1408 0000001010100|1472 0000001010101|1536 0000001011010|1600 0000001011011|1664 0000001100100|1728 0000001100101"""
EXT="""1792 00000001000|1856 00000001100|1920 00000001101|1984 000000010010|2048 000000010011|2112 000000010100|2176 000000010101|2240 000000010110|2304 000000010111|2368 000000011100|2432 000000011101|2496 000000011110|2560 000000011111"""
def tab(s):return {c:int(r) for r,c in (x.split() for x in s.split('|'))}
W=tab(WT)|tab(EXT);B=tab(BT)|tab(EXT)
MODES={'0001':'P','001':'H','1':'V0','011':'VR1','000011':'VR2','0000011':'VR3','010':'VL1','000010':'VL2','0000010':'VL3'}
def decode(data,cols,rows):
    bits=''.join(f'{b:08b}' for b in data);pos=0
    def code(table):
        nonlocal pos
        for L in range(2,14):
            c=bits[pos:pos+L]
            if c in table:pos+=L;return table[c]
        raise ValueError(f'bad code at {pos}')
    def run(table):
        tot=0
        while True:
            r=code(table);tot+=r
            if r<64:return tot
    ref=[cols,cols];out=[]
    for y in range(rows):
        cur=[];a0=-1;color=0
        def b12(a0,color):
            # b1: first changing element on ref line > a0 with colour opposite to current colour
            i=0
            while i<len(ref) and (ref[i]<=a0 or (i%2)!=color):i+=1
            b1=ref[i] if i<len(ref) else cols
            b2=ref[i+1] if i+1<len(ref) else cols
            return b1,b2
        while a0<cols:
            m=None
            for L in range(1,8):
                c=bits[pos:pos+L]
                if c in MODES:m=MODES[c];pos+=L;break
            if m is None:raise ValueError(f'bad mode row {y} pos {pos}')
            b1,b2=b12(a0,color)
            if m=='P':a0=b2
            elif m=='H':
                st=max(a0,0)
                r1=run(W if color==0 else B);r2=run(B if color==0 else W)
                a1=st+r1;a2=a1+r2;cur+= [a1,a2];a0=a2
            else:
                d={'V0':0,'VR1':1,'VR2':2,'VR3':3,'VL1':-1,'VL2':-2,'VL3':-3}[m]
                a1=b1+d;cur.append(a1);a0=a1;color^=1
        cur=[min(x,cols) for x in cur]
        out.append(cur);ref=cur+[cols,cols]
    return out
def png(path,w,h,rowsbytes):
    raw=b''.join(b'\x00'+r for r in rowsbytes)
    def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    open(path,'wb').write(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(raw,6))+chunk(b'IEND',b''))
def main(pdf,outdir,pages):
    data=open(pdf,'rb').read();want={int(p) for p in pages.split(',')}
    objs={int(m.group(1)):m.group(2) for m in re.finditer(rb'(\d+) 0 obj(.*?)endobj',data,re.S)}
    for k,body in objs.items():
        if b'CCITTFaxDecode' not in body:continue
        name=int(re.search(rb'/Name /im(\d+)',body).group(1))
        if name not in want:continue
        cols=int(re.search(rb'/Width (\d+)',body).group(1));rows=int(re.search(rb'/Height (\d+)',body).group(1))
        L=re.search(rb'/Length (\d+)( 0 R)?',body);n=int(L.group(1))
        if L.group(2):n=int(re.search(rb'(\d+)',objs[n]).group(1))
        s=body.index(b'stream')+6
        while body[s:s+1] in b'\r\n':s+=1
        lines=decode(body[s:s+n],cols,rows)
        # 2x downsample: average 2x2 black counts
        rb=[]
        for y in range(0,rows-1,2):
            acc=[0]*(cols//2)
            for yy in (y,y+1):
                ch=lines[yy];x=0;color=0
                for c in ch+[cols]:
                    if color:  # black span x..c
                        for px in range(x,min(c,cols)):acc[px>>1]+=1
                    x=c;color^=1
                    if x>=cols:break
            rb.append(bytes(255-min(255,a*64) for a in acc))
        png(f'{outdir}/p{name:02d}.png',cols//2,len(rb),rb);print('page',name,flush=True)
if __name__=='__main__':main(*sys.argv[1:])
