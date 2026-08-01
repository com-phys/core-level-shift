const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  ImageRun, Header, Footer, PageNumber, PageBreak, VerticalAlign
} = require('docx');

const root = '/Users/behnamazizi/Downloads/core level shifts';
const planar = path.join(root, 'planar');
const pldc = path.join(root, 'planarCOOH');
const output = path.join(pldc, 'report', 'Full_Planar_PLDC_All_Carbon_CLS_Report.docx');
const planarFigure = path.join(planar, 'figures', 'Planar_carbon_groups.png');
const pldcFigure = path.join(pldc, 'figures', 'PLDC_COOH_carbon_groups.png');
const envelopeFigure = path.join(pldc, 'figures', 'planar_vs_PLDC_COOH_all_carbon_envelopes_zoomed.png');
const meanFigure = path.join(pldc, 'figures', 'planar_vs_PLDC_COOH_group_means_split.png');
const summaryCsv = path.join(pldc, 'output', 'planar_vs_PLDC_COOH_group_summary.csv');

function readCsv(file) {
  const lines = fs.readFileSync(file, 'utf8').trim().split(/\r?\n/);
  const headers = lines.shift().split(',');
  return lines.map(line => Object.fromEntries(line.split(',').map((v, i) => [headers[i], v])));
}
const data = readCsv(summaryCsv);
const order = ['C_L_alpha','C_alpha','C_M','C_L_beta','C_beta','C_b','C_w','C_COOH'];
const labels = {C_L_alpha:'C_L,alpha',C_alpha:'C_alpha',C_M:'C_M',C_L_beta:'C_L,beta',C_beta:'C_beta',C_b:'C_b',C_w:'C_w',C_COOH:'C_COOH'};
const descriptions = {
  C_L_alpha:'User-defined ligand alpha-carbon sites',
  C_alpha:'User-defined porphyrin alpha-carbon sites',
  C_M:'Meso bridge carbon sites',
  C_L_beta:'User-defined ligand beta-carbon sites',
  C_beta:'User-defined porphyrin beta-carbon sites',
  C_b:'Benzene/phenyl carbon subset C_b',
  C_w:'Remaining phenyl carbon subset C_w',
  C_COOH:'Added carboxyl carbon atoms in PLDC–COOH',
};
const indices = {
  C_L_alpha:'4, 5, 42, 43', C_alpha:'20, 21, 26, 27', C_M:'6, 13, 28, 35',
  C_L_beta:'2, 3, 44, 45', C_beta:'22, 23, 24, 25',
  C_b:'14–19, 29–34', C_w:'7–12, 36–41', C_COOH:'76, 79',
};

const navy='17365D', blue='2F75B5', gray='626D78', pale='F5F8FB';
const borders={top:{style:BorderStyle.SINGLE,size:4,color:'B7C3D0'},bottom:{style:BorderStyle.SINGLE,size:4,color:'B7C3D0'},left:{style:BorderStyle.SINGLE,size:4,color:'B7C3D0'},right:{style:BorderStyle.SINGLE,size:4,color:'B7C3D0'},insideHorizontal:{style:BorderStyle.SINGLE,size:3,color:'D9E0E7'},insideVertical:{style:BorderStyle.SINGLE,size:3,color:'D9E0E7'}};
const pageBreak=()=>new Paragraph({children:[new PageBreak()]});
const p=(text,o={})=>new Paragraph({alignment:o.align||AlignmentType.LEFT,spacing:{after:o.after===undefined?105:o.after,line:o.line||276},keepNext:!!o.keepNext,children:[new TextRun({text,bold:!!o.bold,italics:!!o.italics,color:o.color,size:o.size||20})]});
const h=(text,level=HeadingLevel.HEADING_1)=>new Paragraph({heading:level,spacing:{before:level===HeadingLevel.HEADING_1?190:135,after:75},children:[new TextRun(text)]});
const caption=(text)=>new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:40,after:110},children:[new TextRun({text,italics:true,color:gray,size:17})]});

function cell(text,width,header=false,align=AlignmentType.LEFT,size=17){
  return new TableCell({width:{size:width,type:WidthType.DXA},verticalAlign:VerticalAlign.CENTER,shading:header?{fill:navy,type:ShadingType.CLEAR}:undefined,margins:{top:62,bottom:62,left:68,right:68},children:[new Paragraph({alignment:align,spacing:{after:0},children:[new TextRun({text:String(text),bold:header,color:header?'FFFFFF':'222222',size})]})]});
}
function keyValueTable(rows){
  return new Table({width:{size:9360,type:WidthType.DXA},columnWidths:[2450,6910],borders,rows:rows.map(([a,b],i)=>new TableRow({children:[new TableCell({width:{size:2450,type:WidthType.DXA},shading:{fill:i%2?'EDF3F8':'DDEAF5',type:ShadingType.CLEAR},margins:{top:62,bottom:62,left:72,right:72},children:[new Paragraph({spacing:{after:0},children:[new TextRun({text:a,bold:true,color:navy,size:17})]})]}),new TableCell({width:{size:6910,type:WidthType.DXA},shading:{fill:i%2?'FFFFFF':'F8FAFC',type:ShadingType.CLEAR},margins:{top:62,bottom:62,left:72,right:72},children:[new Paragraph({spacing:{after:0},children:[new TextRun({text:b,size:17})]})]})]}))});
}
function imageParagraph(file,width,height,alt){
  return new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:55},children:[new ImageRun({data:fs.readFileSync(file),transformation:{width,height},type:'png',altText:{title:alt,description:alt,name:alt}})]});
}
function step(title,body){
  return [new Paragraph({spacing:{before:80,after:35},keepNext:true,children:[new TextRun({text:title,bold:true,color:blue,size:20})]}),p(body,{after:80})];
}

const groupWidths=[1250,2650,2450,3010];
const groupRows=[new TableRow({tableHeader:true,children:[cell('Group',groupWidths[0],true),cell('Meaning',groupWidths[1],true),cell('Planar indices',groupWidths[2],true),cell('PLDC–COOH indices',groupWidths[3],true)]})];
for(const group of order){
  groupRows.push(new TableRow({children:[cell(labels[group],groupWidths[0]),cell(descriptions[group],groupWidths[1]),cell(group==='C_COOH'?'—':indices[group],groupWidths[2]),cell(indices[group],groupWidths[3])] }));
}

const resultWidths=[1280,920,1280,1280,920,1280,1280,1120];
const resultRows=[new TableRow({tableHeader:true,children:[cell('Group',resultWidths[0],true),cell('n P',resultWidths[1],true,AlignmentType.CENTER),cell('Planar mean',resultWidths[2],true,AlignmentType.CENTER),cell('Planar σ',resultWidths[3],true,AlignmentType.CENTER),cell('n D',resultWidths[4],true,AlignmentType.CENTER),cell('PLDC mean',resultWidths[5],true,AlignmentType.CENTER),cell('PLDC σ',resultWidths[6],true,AlignmentType.CENTER),cell('Δ mean',resultWidths[7],true,AlignmentType.CENTER)]})];
for(const group of order){
  const a=data.find(r=>r.structure==='Planar'&&r.group===group);
  const b=data.find(r=>r.structure==='PLDC-COOH'&&r.group===group);
  const delta=a&&b?Number(b.mean_cls_eV)-Number(a.mean_cls_eV):null;
  resultRows.push(new TableRow({children:[cell(labels[group],resultWidths[0]),cell(a?a.multiplicity:'—',resultWidths[1],false,AlignmentType.CENTER),cell(a?Number(a.mean_cls_eV).toFixed(3):'—',resultWidths[2],false,AlignmentType.CENTER),cell(a?Number(a.std_cls_eV).toFixed(3):'—',resultWidths[3],false,AlignmentType.CENTER),cell(b?b.multiplicity:'—',resultWidths[4],false,AlignmentType.CENTER),cell(b?Number(b.mean_cls_eV).toFixed(3):'—',resultWidths[5],false,AlignmentType.CENTER),cell(b?Number(b.std_cls_eV).toFixed(3):'—',resultWidths[6],false,AlignmentType.CENTER),cell(delta===null?'—':`${delta>=0?'+':''}${delta.toFixed(3)}`,resultWidths[7],false,AlignmentType.CENTER)]}));
}

const parameterWidths=[1760,1620,3820,2160];
const parameterRows=[new TableRow({tableHeader:true,children:[cell('Parameter',parameterWidths[0],true),cell('Value',parameterWidths[1],true),cell('Reason for selection',parameterWidths[2],true),cell('Caution',parameterWidths[3],true)]})];
[
  ['Functional','PBE','Matches the exchange–correlation form used to generate the selected pseudopotentials and provides a consistent comparison.','A functional-sensitivity study was not performed.'],
  ['Cell','25 Å cubic','Keeps both molecules in the same supercell; the protonated PLDC geometry retains about 7 Å nearest-image separation along its longest direction.','Cell-size convergence should be checked for publication.'],
  ['Isolation','Martyna–Tuckerman','Reduces electrostatic interaction between periodic replicas of an isolated molecule.','Does not replace a cell-size test.'],
  ['k points','Γ only','An isolated molecule in a large cubic supercell has no meaningful band dispersion.','Appropriate only for the molecular-supercell model.'],
  ['Cutoffs','30 / 180 Ry','Working values already demonstrated for the Planar pseudopotential set; 180 Ry is six times the wavefunction cutoff for ultrasoft augmentation density.','No independent cutoff-convergence series was run.'],
  ['Smearing','MV, 0.02 Ry','Stabilizes occupation of closely spaced frontier states during SCF while applying the same treatment to both structures.','The value is a numerical aid, not a physical temperature.'],
  ['Mixing','local-TF, β=0.20','This setting converged the Planar system and was retained unchanged for a controlled comparison.','PLDC still required 40 iterations.'],
  ['Threshold','1×10⁻⁶ Ry','Provides a tight and consistent electronic convergence criterion for site-shift post-processing.','Stricter thresholds would increase runtime.'],
  ['Symmetry','nosym/noinv','Preserves atom-by-atom distinctions and prevents symmetry reduction from merging nominally separate sites.','Increases computational work.'],
  ['Broadening','0.35 eV FWHM','Produces a smooth, visually comparable C 1s envelope consistent with the earlier plotting convention.','Post-processing only; not calculated lifetime broadening.'],
].forEach(r=>parameterRows.push(new TableRow({children:r.map((x,i)=>cell(x,parameterWidths[i],false,AlignmentType.LEFT,16))})));

const doc=new Document({
  styles:{default:{document:{run:{font:'Arial',size:20,color:'222222'},paragraph:{spacing:{after:105,line:276}}}},paragraphStyles:[
    {id:'Title',name:'Title',basedOn:'Normal',next:'Normal',run:{font:'Arial',size:42,bold:true,color:navy},paragraph:{alignment:AlignmentType.CENTER,spacing:{after:125}}},
    {id:'Subtitle',name:'Subtitle',basedOn:'Normal',next:'Normal',run:{font:'Arial',size:22,color:gray},paragraph:{alignment:AlignmentType.CENTER,spacing:{after:170}}},
    {id:'Heading1',name:'Heading 1',basedOn:'Normal',next:'Normal',quickFormat:true,run:{font:'Arial',size:28,bold:true,color:navy},paragraph:{keepNext:true,spacing:{before:190,after:75},outlineLevel:0}},
    {id:'Heading2',name:'Heading 2',basedOn:'Normal',next:'Normal',quickFormat:true,run:{font:'Arial',size:22,bold:true,color:blue},paragraph:{keepNext:true,spacing:{before:135,after:65},outlineLevel:1}}
  ]},
  sections:[{properties:{page:{size:{width:12240,height:15840},margin:{top:840,right:880,bottom:790,left:880,header:380,footer:380}}},headers:{default:new Header({children:[new Paragraph({alignment:AlignmentType.RIGHT,spacing:{after:0},children:[new TextRun({text:'FULL TECHNICAL REPORT · C 1s CORE-LEVEL SHIFTS',color:'7A8793',size:14})]})]})},footers:{default:new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:0},children:[new TextRun({text:'Planar and PLDC–COOH  |  ',color:'7A8793',size:15}),new TextRun({children:[PageNumber.CURRENT],color:'7A8793',size:15})]})]})},children:[
    new Paragraph({style:'Title',children:[new TextRun('Planar and Protonated PLDC')]}),
    new Paragraph({style:'Title',children:[new TextRun('All-Carbon Core-Level Shifts')]}),
    new Paragraph({style:'Subtitle',children:[new TextRun('Quantum ESPRESSO initial-state calculation, atom grouping, parameter rationale, spectra, and runtime')]}),
    p('Prepared 1 August 2026',{align:AlignmentType.CENTER,color:gray,size:18,after:170}),
    new Table({width:{size:9000,type:WidthType.DXA},columnWidths:[4500,4500],borders:{top:{style:BorderStyle.NONE},bottom:{style:BorderStyle.NONE},left:{style:BorderStyle.NONE},right:{style:BorderStyle.NONE},insideHorizontal:{style:BorderStyle.NONE},insideVertical:{style:BorderStyle.NONE}},rows:[new TableRow({children:[new TableCell({width:{size:4500,type:WidthType.DXA},children:[imageParagraph(planarFigure,285,219,'Planar molecular groups'),p('Planar: ZnC44H28N4',{align:AlignmentType.CENTER,bold:true,size:17})]}),new TableCell({width:{size:4500,type:WidthType.DXA},children:[imageParagraph(pldcFigure,285,228,'PLDC molecular groups'),p('PLDC–COOH: ZnC46H28N4O4',{align:AlignmentType.CENTER,bold:true,size:17})]})]})]}),
    h('Executive summary'),
    p('This report documents initial-state C 1s core-level shifts for a 77-atom Planar Zn-porphyrin and an 83-atom protonated PLDC derivative. The PLDC model contains two added carboxyl groups and two constructed O–H bonds. All 44 carbon atoms in Planar and all 46 carbon atoms in PLDC–COOH were evaluated.'),
    p('The Planar SCF converged in 32 iterations and 15 min 05 s. PLDC–COOH converged in 40 iterations and 1 h 38 min. The same PBE functional, 25 Å cell, 30/180 Ry cutoffs, Γ-point sampling, molecular isolation correction, smearing, and convergence threshold were used to make the relative comparison controlled.'),
    p('The largest separate feature belongs to the two PLDC carboxyl carbons, C_COOH, with mean shift −3.678 eV under the Quantum ESPRESSO convention ΔE = IS(reference) − IS(site).'),

    pageBreak(), h('1. Planar structure and named carbon groups'),
    imageParagraph(planarFigure,650,500,'Planar molecule with named carbon groups and indices'),
    caption('Figure 1. Planar molecule. Carbon color identifies the assigned group; the number inside each carbon is its one-based XYZ atom index.'),
    p('The Planar structure contains 44 carbon atoms divided into seven user-defined groups. Nitrogen atoms N46–N49 and Zn1 are shown for orientation but are not included in the all-carbon comparison plotted in this report.'),

    pageBreak(), h('2. Protonated PLDC structure and named carbon groups'),
    imageParagraph(pldcFigure,650,520,'Protonated PLDC molecule with named carbon groups and indices'),
    caption('Figure 2. Protonated PLDC–COOH molecule. The common Planar group numbering is retained; C76 and C79 are the added carboxyl carbon atoms.'),
    p('The supplied PLDC geometry originally contained four oxygen atoms but no acidic hydrogen atoms. One hydrogen was added to the longer C–O bond in each carboxyl group: H82–O78 and H83–O80, both with O–H = 0.98 Å. This produces a neutral ZnC46H28N4O4 single-point model. The new proton positions were not geometry-optimized.'),

    pageBreak(), h('3. Carbon-group definitions'),
    p('The following assignments were applied identically to both structures wherever the corresponding atom exists. C_COOH occurs only in PLDC–COOH.'),
    new Table({width:{size:9360,type:WidthType.DXA},columnWidths:groupWidths,borders,rows:groupRows}),
    h('Why the same indexing can be used',HeadingLevel.HEADING_2),
    p('Atoms 1–75 of the protonated PLDC file preserve the Zn-porphyrin framework and common carbon ordering. The two new carboxyl carbons are appended as atoms 76 and 79, with their oxygen atoms 77–78 and 80–81. The added protons are atoms 82 and 83. Therefore the original Planar group definitions can be transferred without renumbering the common carbon sites.'),
    h('Reference population',HeadingLevel.HEADING_2),
    p('The internal reference is the mean initial-state contribution of all 24 peripheral C_b and C_w atoms in each molecule. Using the same reference definition independently within each structure removes a common offset and focuses the comparison on relative chemical shifts.'),

    pageBreak(), h('4. How the core-level shifts were calculated'),
    ...step('Step 1 — Prepare the molecular supercell','Each XYZ geometry was placed in a 25 Å cubic supercell. Γ-point sampling and the Martyna–Tuckerman isolated-system correction were selected because the target is an isolated molecule rather than a periodic crystal.'),
    ...step('Step 2 — Define normal and core-excited carbon species','The SCF input includes normal carbon C with C.pbe-rrkjus.UPF and an auxiliary core-excited carbon species Cs with C.star1s-pbe-rrkjus.UPF. The molecular coordinates use the normal C label; the excited species is included so initial_state.x can evaluate the normal-to-core-excited pseudopotential change for every requested carbon site.'),
    ...step('Step 3 — Run a self-consistent ground-state calculation','pw.x solves the Kohn–Sham equations using PBE, ultrasoft/vanadium-type pseudopotentials, 30 Ry wavefunction and 180 Ry density cutoffs, Marzari–Vanderbilt smearing, and local-TF charge mixing. The SCF density is converged before any site shifts are extracted.'),
    ...step('Step 4 — Evaluate site contributions with initial_state.x','For Planar, excite(2)=5 maps normal C to Cs; the earlier Planar run also mapped N to a core-excited N auxiliary species. For PLDC–COOH, excite(2)=6 maps normal C to Cs. initial_state.x then reports the initial-state contribution for every atom of the mapped normal species.'),
    ...step('Step 5 — Convert contributions into relative shifts','For carbon atom i, the reported value is ΔE_i = mean[IS(C_b+C_w)] − IS_i. This is the reference-minus-site sign used by the Quantum ESPRESSO CLS_IS_example. Positive and negative shifts therefore indicate position relative to the chosen internal carbon reference; they are not absolute C 1s binding energies.'),
    ...step('Step 6 — Build spectra','Each discrete carbon shift contributes a unit-area Gaussian, G_i(E)=exp[−4 ln(2)((E−ΔE_i)/FWHM)^2], with FWHM = 0.35 eV. Curves are summed by group. The blue background combines C_L,alpha+C_alpha; the amber background combines all remaining groups. Individual groups are drawn in front and no total line is shown.'),
    h('Pseudopotentials used',HeadingLevel.HEADING_2),
    keyValueTable([
      ['Zn','Zn.pbe-van.UPF'],['C / core-excited C','C.pbe-rrkjus.UPF / C.star1s-pbe-rrkjus.UPF'],
      ['N','N.pbe-van_ak.UPF'],['H','H.pbe-rrkjus.UPF'],['O','O.pbe-rrkjus.UPF']
    ]),

    pageBreak(), h('5. Parameter choices and rationale'),
    p('The objective was a controlled difference between the two molecules. Consequently, numerical settings were kept identical wherever possible. The choices below are working settings validated by successful SCF convergence, not a completed publication-level convergence study.'),
    new Table({width:{size:9360,type:WidthType.DXA},columnWidths:parameterWidths,borders,rows:parameterRows}),

    pageBreak(), h('6. Convergence behavior and elapsed time'),
    keyValueTable([
      ['Planar system','77 atoms, 236 electrons, 142 Kohn–Sham states'],
      ['PLDC–COOH system','83 atoms, 268 electrons, 161 Kohn–Sham states'],
      ['Planar SCF','32 iterations; final energy −739.91431933 Ry; 15 min 05 s wall'],
      ['Planar initial_state.x','13.14 s wall'],
      ['PLDC–COOH SCF','40 iterations; final energy −890.04265055 Ry; estimated accuracy 5.6×10⁻⁷ Ry'],
      ['PLDC–COOH initial_state.x','1 min 06 s wall'],
      ['PLDC total analyzed workflow','Approximately 1 h 39 min for SCF plus initial_state.x'],
      ['Parallel execution','4 MPI processes on the local laptop']
    ]),
    h('Why PLDC took longer',HeadingLevel.HEADING_2),
    p('PLDC–COOH has six additional atoms, 32 additional valence electrons, and 19 additional Kohn–Sham states. Oxygen introduces additional occupied states and ultrasoft augmentation work. Several frontier eigenvalues also required extra Davidson iterations late in the SCF cycle. Together these effects increased the wall time from about 15 minutes for Planar to 1 hour 38 minutes for PLDC–COOH.'),
    h('Convergence evidence',HeadingLevel.HEADING_2),
    p('Planar reached the requested 1×10⁻⁶ Ry SCF criterion after 32 iterations. PLDC–COOH required 40 iterations and finished with an estimated SCF accuracy of 5.6×10⁻⁷ Ry. Both outputs ended with “convergence has been achieved” and “JOB DONE.” The longer PLDC run was retained in full, including its 424 MB restart directory.'),

    pageBreak(), h('7. Numerical core-level-shift results'),
    p('Table 3 reports group means and standard deviations in eV. Δ mean is PLDC–COOH minus Planar. All values use the same group definition and the molecule-specific mean(C_b+C_w) reference.'),
    new Table({width:{size:9360,type:WidthType.DXA},columnWidths:resultWidths,borders,rows:resultRows}),
    caption('Table 3. Group-averaged C 1s initial-state shifts. P = Planar; D = PLDC–COOH; σ is the population standard deviation across atoms in the group.'),
    imageParagraph(meanFigure,650,343,'Group mean shift comparison'),
    caption('Figure 3. Mean shifts with whiskers spanning the minimum and maximum site values. C_COOH is separated because its scale is far from the common groups.'),
    h('Main numerical changes',HeadingLevel.HEADING_2),
    p('Relative to Planar, PLDC–COOH shifts C_L,alpha by −0.079 eV and C_alpha by −0.111 eV. C_M moves by +0.246 eV. C_L,beta and C_beta change by −0.033 and −0.040 eV. The C_b and C_w means move in opposite directions by approximately −0.052 and +0.052 eV because their combined mean defines zero. The new C_COOH group appears at −3.678 eV.'),

    pageBreak(), h('8. Gaussian-broadened C 1s envelopes'),
    imageParagraph(envelopeFigure,650,495,'All-carbon spectral envelope comparison'),
    caption('Figure 4. Gaussian-broadened C 1s initial-state shifts. Blue background: C_L,alpha+C_alpha. Amber background: all remaining carbon groups. Individual groups are foreground curves. No total curve is included.'),
    h('Reading the envelopes',HeadingLevel.HEADING_2),
    p('The Planar alpha-pair envelope is narrow because its eight sites are nearly equivalent. PLDC–COOH broadens and splits this negative-shift region, consistent with reduced equivalence after adding the two carboxyl groups. The remaining-group background is dominated by C_b and C_w because each contains 12 atoms. The two C_COOH atoms have a much smaller integrated weight and are displayed in an inset around −3.68 eV.'),
    h('Normalization',HeadingLevel.HEADING_2),
    p('Within each molecular panel, all group curves use a common scale derived from the main-window summed intensity. The relative heights therefore preserve group multiplicity within that molecule. Each panel is normalized separately, so peak heights should not be interpreted as an absolute cross-section comparison between Planar and PLDC.'),

    pageBreak(), h('9. Interpretation, limitations, and recommended next steps'),
    h('Interpretation boundaries',HeadingLevel.HEADING_2),
    p('These are initial-state relative shifts derived from the self-consistent electrostatic environment and the normal/core-excited pseudopotential pair. They are not absolute experimental binding energies. Direct comparison with XPS normally requires an energy alignment and may require final-state screening, relaxation, instrumental broadening, and cross-section weighting.'),
    h('Geometry limitation',HeadingLevel.HEADING_2),
    p('The Planar and supplied PLDC frameworks were used as provided. H82 and H83 were constructed geometrically and were not relaxed. The C_COOH values are therefore especially sensitive to a future geometry optimization of the O–H and C–O bond lengths.'),
    h('Numerical limitations',HeadingLevel.HEADING_2),
    p('A systematic convergence study of cell size, ecutwfc, ecutrho, smearing, and pseudopotential family was not performed. The 25 Å and 30/180 Ry settings are demonstrated working parameters. Before publication, repeat representative calculations at larger cells and cutoffs and verify that relative group means change less than the chosen tolerance, for example 0.02–0.05 eV.'),
    h('Recommended next steps',HeadingLevel.HEADING_2),
    p('First optimize the neutral PLDC–COOH geometry while preserving the intended molecular state. Then perform cell/cutoff convergence tests on representative carbon sites, recalculate the all-carbon shifts, and align the simulated spectrum to a selected experimental or calculated reference peak. If absolute XPS energies are required, add a final-state or ΔSCF workflow.'),
    h('Conclusion',HeadingLevel.HEADING_2),
    p('The requested all-carbon comparison is complete and reproducible. Both structures were treated with consistent electronic settings. PLDC–COOH changes the alpha and meso regions, broadens several common groups, and adds a well-separated two-carbon C_COOH feature under the Quantum ESPRESSO initial-state convention.'),

    pageBreak(), h('10. Reproducibility and file inventory'),
    keyValueTable([
      ['Main result directory',pldc],
      ['Planar geometry',path.join(planar,'structure','planar.xyz')],
      ['PLDC–COOH geometry',path.join(pldc,'structure','PLDC_COOH.xyz')],
      ['PLDC inputs',path.join(pldc,'input')],
      ['PLDC outputs',path.join(pldc,'output')],
      ['Restart data',path.join(pldc,'output','restart_data','pldc_cooh_allC.save')],
      ['Per-atom data',path.join(pldc,'output','planar_vs_PLDC_COOH_all_carbon_atom_shifts.csv')],
      ['Group summary',summaryCsv],
      ['Reproduction scripts',path.join(pldc,'script')]
    ]),
    h('Software commands',HeadingLevel.HEADING_2),
    p('SCF: mpirun −np 4 pw.x −in pldc_cooh_allC.scf.in'),
    p('Initial state: mpirun −np 4 initial_state.x −in pldc_cooh_allC.istate.in'),
    p('Analysis: python3 analyze_compare_planar_pldc_allC.py'),
    h('References',HeadingLevel.HEADING_2),
    p('1. P. Giannozzi et al., Journal of Physics: Condensed Matter 21, 395502 (2009).'),
    p('2. P. Giannozzi et al., Journal of Physics: Condensed Matter 29, 465901 (2017).'),
    p('3. P. Giannozzi et al., Journal of Chemical Physics 152, 154105 (2020).'),
    p('4. J. P. Perdew, K. Burke, and M. Ernzerhof, Physical Review Letters 77, 3865 (1996).'),
    p('5. Quantum ESPRESSO PP example CLS_IS_example/run_example, reference-minus-site initial-state shift convention.'),
    p('All machine-readable results, figures, calculation inputs, outputs, and restart data are retained in the organized package.',{italics:true,color:gray})
  ]}]
});

Packer.toBuffer(doc).then(buffer=>{fs.writeFileSync(output,buffer);console.log(output);});
