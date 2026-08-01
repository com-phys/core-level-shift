const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  ImageRun, Header, Footer, PageNumber, PageBreak, VerticalAlign
} = require('docx');

const pkg = '/Users/behnamazizi/Downloads/core level shifts/planar';
const root = path.join(pkg, 'comparison', 'core_level_shifts');
const out = path.join(root, 'Planar_PLDC_All_Carbon_CLS_Report.docx');
const envelope = path.join(root, 'planar_vs_PLDC_COOH_all_carbon_envelopes_zoomed.png');
const meansPlot = path.join(root, 'planar_vs_PLDC_COOH_group_means_split.png');
const csvPath = path.join(root, 'planar_vs_PLDC_COOH_group_summary.csv');

function readCsv(file) {
  const lines = fs.readFileSync(file, 'utf8').trim().split(/\r?\n/);
  const headers = lines.shift().split(',');
  return lines.map(line => Object.fromEntries(line.split(',').map((v,i) => [headers[i],v])));
}
const data = readCsv(csvPath);
const order = ['C_L_alpha','C_alpha','C_M','C_L_beta','C_beta','C_b','C_w','C_COOH'];
const labels = {C_L_alpha:'C_L,alpha', C_alpha:'C_alpha', C_M:'C_M', C_L_beta:'C_L,beta', C_beta:'C_beta', C_b:'C_b', C_w:'C_w', C_COOH:'C_COOH'};
const navy='17365D', blue='2F75B5', gray='666666';
const borders={top:{style:BorderStyle.SINGLE,size:4,color:'B7C3D0'},bottom:{style:BorderStyle.SINGLE,size:4,color:'B7C3D0'},left:{style:BorderStyle.SINGLE,size:4,color:'B7C3D0'},right:{style:BorderStyle.SINGLE,size:4,color:'B7C3D0'},insideHorizontal:{style:BorderStyle.SINGLE,size:3,color:'D9E0E7'},insideVertical:{style:BorderStyle.SINGLE,size:3,color:'D9E0E7'}};

const p=(text,o={})=>new Paragraph({alignment:o.align||AlignmentType.LEFT,spacing:{after:o.after===undefined?105:o.after,line:276},children:[new TextRun({text,bold:!!o.bold,italics:!!o.italics,color:o.color,size:o.size||20})]});
const h=(text,level=HeadingLevel.HEADING_1)=>new Paragraph({heading:level,spacing:{before:190,after:80},children:[new TextRun(text)]});
function cell(text,width,header=false,align=AlignmentType.LEFT){return new TableCell({width:{size:width,type:WidthType.DXA},verticalAlign:VerticalAlign.CENTER,shading:header?{fill:navy,type:ShadingType.CLEAR}:undefined,margins:{top:65,bottom:65,left:70,right:70},children:[new Paragraph({alignment:align,spacing:{after:0},children:[new TextRun({text:String(text),bold:header,color:header?'FFFFFF':'222222',size:17})]})]});}
function info(rows){return new Table({width:{size:9360,type:WidthType.DXA},columnWidths:[2450,6910],borders,rows:rows.map(([a,b],i)=>new TableRow({children:[new TableCell({width:{size:2450,type:WidthType.DXA},shading:{fill:i%2?'EDF3F8':'DDEAF5',type:ShadingType.CLEAR},margins:{top:65,bottom:65,left:75,right:75},children:[new Paragraph({spacing:{after:0},children:[new TextRun({text:a,bold:true,color:navy,size:17})]})]}),new TableCell({width:{size:6910,type:WidthType.DXA},shading:{fill:i%2?'FFFFFF':'F8FAFC',type:ShadingType.CLEAR},margins:{top:65,bottom:65,left:75,right:75},children:[new Paragraph({spacing:{after:0},children:[new TextRun({text:b,size:17})]})]})]}))});}

const widths=[1420,1000,1470,1470,1470,2530];
const tableRows=[new TableRow({tableHeader:true,children:[cell('Group',widths[0],true),cell('Planar n',widths[1],true,AlignmentType.CENTER),cell('Planar mean',widths[2],true,AlignmentType.CENTER),cell('PLDC n',widths[3],true,AlignmentType.CENTER),cell('PLDC mean',widths[4],true,AlignmentType.CENTER),cell('PLDC range (eV)',widths[5],true,AlignmentType.CENTER)]})];
for(const group of order){
  const a=data.find(r=>r.structure==='Planar'&&r.group===group);
  const b=data.find(r=>r.structure==='PLDC-COOH'&&r.group===group);
  tableRows.push(new TableRow({children:[cell(labels[group],widths[0]),cell(a?a.multiplicity:'—',widths[1],false,AlignmentType.CENTER),cell(a?Number(a.mean_cls_eV).toFixed(3):'—',widths[2],false,AlignmentType.CENTER),cell(b?b.multiplicity:'—',widths[3],false,AlignmentType.CENTER),cell(b?Number(b.mean_cls_eV).toFixed(3):'—',widths[4],false,AlignmentType.CENTER),cell(b?`${Number(b.min_cls_eV).toFixed(3)} to ${Number(b.max_cls_eV).toFixed(3)}`:'—',widths[5],false,AlignmentType.CENTER)]}));
}

const doc=new Document({
  styles:{default:{document:{run:{font:'Arial',size:20,color:'222222'},paragraph:{spacing:{after:105,line:276}}}},paragraphStyles:[
    {id:'Title',name:'Title',basedOn:'Normal',next:'Normal',run:{font:'Arial',size:40,bold:true,color:navy},paragraph:{alignment:AlignmentType.CENTER,spacing:{after:120}}},
    {id:'Subtitle',name:'Subtitle',basedOn:'Normal',next:'Normal',run:{font:'Arial',size:21,color:gray},paragraph:{alignment:AlignmentType.CENTER,spacing:{after:160}}},
    {id:'Heading1',name:'Heading 1',basedOn:'Normal',next:'Normal',quickFormat:true,run:{font:'Arial',size:27,bold:true,color:navy},paragraph:{keepNext:true,spacing:{before:190,after:80},outlineLevel:0}},
    {id:'Heading2',name:'Heading 2',basedOn:'Normal',next:'Normal',quickFormat:true,run:{font:'Arial',size:22,bold:true,color:blue},paragraph:{keepNext:true,spacing:{before:140,after:65},outlineLevel:1}}
  ]},
  sections:[{properties:{page:{size:{width:12240,height:15840},margin:{top:850,right:900,bottom:800,left:900,header:380,footer:380}}},headers:{default:new Header({children:[new Paragraph({alignment:AlignmentType.RIGHT,spacing:{after:0},children:[new TextRun({text:'QUANTUM ESPRESSO · C 1s COMPARISON',color:'7A8793',size:15})]})]})},footers:{default:new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:0},children:[new TextRun({text:'Planar–PLDC all-carbon report  |  ',color:'7A8793',size:15}),new TextRun({children:[PageNumber.CURRENT],color:'7A8793',size:15})]})]})},children:[
    new Paragraph({style:'Title',children:[new TextRun('Planar versus Protonated PLDC')]}),
    new Paragraph({style:'Title',children:[new TextRun('All-Carbon Core-Level Shifts')]}),
    new Paragraph({style:'Subtitle',children:[new TextRun('Initial-state Quantum ESPRESSO comparison · all carbon groups')]}),
    new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:130},children:[new TextRun({text:'1 August 2026',size:18,color:gray})]}),
    new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:110},children:[new ImageRun({data:fs.readFileSync(envelope),transformation:{width:665,height:507},type:'png',altText:{title:'Planar and PLDC carbon envelopes',description:'All-carbon C 1s initial-state shift envelopes for Planar and protonated PLDC with a COOH inset.',name:'CLS envelopes'}})]}),
    h('Result summary'),
    p('The all-carbon Planar dataset and a new neutral protonated PLDC calculation are complete. The PLDC model contains two COOH groups, with H82 bonded to O78 and H83 bonded to O80. All 44 Planar and all 46 PLDC carbon atoms were evaluated.'),
    p('Every atom contributes a unit-area Gaussian with FWHM = 0.35 eV. The blue background is the combined C_L,alpha + C_alpha envelope; the contrasting amber background contains all remaining carbon groups. Individual group curves are drawn in the foreground, and no total curve is shown. The CSV files contain the discrete Quantum ESPRESSO values.'),

    new Paragraph({children:[new PageBreak()]}),
    h('Carbon-group shifts'),
    p('Shifts use the Quantum ESPRESSO example convention: ΔE = IS(reference) − IS(site). The internal reference is the mean initial-state contribution of all Cb and Cw atoms in the same molecule.'),
    new Table({width:{size:9360,type:WidthType.DXA},columnWidths:widths,borders,rows:tableRows}),
    p('The two PLDC C_COOH atoms form a separated feature with mean shift −3.678 eV (range −3.801 to −3.556 eV). This sign follows the Quantum ESPRESSO initial-state convention above.',{italics:true,color:gray,size:18}),
    new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:90,after:90},children:[new ImageRun({data:fs.readFileSync(meansPlot),transformation:{width:660,height:348},type:'png',altText:{title:'Carbon group mean shifts',description:'Mean carbon shifts and per-group site ranges for Planar and PLDC.',name:'Group means'}})]}),

    new Paragraph({children:[new PageBreak()]}),
    h('Calculation details'),
    info([
      ['Structures','Planar ZnC44H28N4 (77 atoms); PLDC–COOH ZnC46H28N4O4 (83 atoms)'],
      ['Electronic model','Neutral, closed-shell single-point calculations'],
      ['Quantum ESPRESSO','Version 7.5; pw.x followed by initial_state.x'],
      ['Exchange–correlation','PBE'],
      ['Cell / isolation','25 Å cubic cell; Martyna–Tuckerman isolated correction; Γ point'],
      ['Plane-wave cutoffs','30 Ry wave functions; 180 Ry charge density'],
      ['Occupations','Marzari–Vanderbilt smearing, 0.02 Ry'],
      ['Convergence','conv_thr = 1×10⁻⁶ Ry; local-TF mixing, β = 0.20'],
      ['Execution','4 MPI processes']
    ]),
    h('Convergence and runtime',HeadingLevel.HEADING_2),
    info([
      ['Planar SCF','32 iterations; −739.91431933 Ry; 15 min 05 s wall'],
      ['Planar initial_state.x','13.14 s wall'],
      ['PLDC–COOH SCF','40 iterations; −890.04265055 Ry; final accuracy 5.6×10⁻⁷ Ry'],
      ['PLDC–COOH SCF runtime','1 h 38 min wall'],
      ['PLDC–COOH initial_state.x','1 min 06 s wall']
    ]),
    h('Important modeling note',HeadingLevel.HEADING_2),
    p('The two O–H positions were constructed with 0.98 Å bonds by extending the longer C–O direction in each supplied carboxyl group. No geometry optimization was performed after proton placement. The reported PLDC shifts are therefore single-point values for this constructed neutral geometry; geometry optimization and cutoff/cell convergence should precede publication-quality interpretation.'),
    h('Files',HeadingLevel.HEADING_2),
    info([
      ['inputs/','PLDC SCF and initial_state.x input files'],
      ['outputs/','Converged pw.x and initial_state.x output files'],
      ['restart_data/','Quantum ESPRESSO save directory for restarting/post-processing'],
      ['scripts/','Preparation and all-carbon comparison scripts'],
      ['CSV files','Per-atom Planar, PLDC, combined, and group-summary data'],
      ['PNG/PDF files','Full-range, zoomed, and group-mean comparison figures']
    ])
  ]}]
});

Packer.toBuffer(doc).then(buffer=>{fs.writeFileSync(out,buffer);console.log(out);});
