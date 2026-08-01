const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  ImageRun, Header, Footer, PageNumber, PageBreak, VerticalAlign
} = require('docx');

const root = '/Users/behnamazizi/Downloads/core level shifts/planar';
const out = path.join(root, 'Planar_Core_Level_Shift_Report.docx');
const spectrum = path.join(root, 'results', 'planar_selected_C_envelopes.png');
const comparison = path.join(root, 'comparison', 'planar_vs_PLDC_structures.png');

function csvRows(file) {
  const lines = fs.readFileSync(file, 'utf8').trim().split(/\r?\n/);
  const headers = lines.shift().split(',');
  return lines.map(line => Object.fromEntries(line.split(',').map((v, i) => [headers[i], v])));
}

const groups = csvRows(path.join(root, 'results', 'planar_targeted_C_N_group_summary.csv'));
const carbonGroups = groups.filter(r => r.group.startsWith('C'));
const nitrogenGroups = groups.filter(r => r.group.startsWith('N'));

const navy = '17365D';
const blue = '2F75B5';
const lightBlue = 'D9EAF7';
const pale = 'F3F6F9';
const red = 'C94C5C';
const orange = 'ED7D31';
const gray = '666666';
const borders = { top: {style: BorderStyle.SINGLE, size: 4, color: 'B7C3D0'}, bottom: {style: BorderStyle.SINGLE, size: 4, color: 'B7C3D0'}, left: {style: BorderStyle.SINGLE, size: 4, color: 'B7C3D0'}, right: {style: BorderStyle.SINGLE, size: 4, color: 'B7C3D0'}, insideHorizontal: {style: BorderStyle.SINGLE, size: 3, color: 'D9E0E7'}, insideVertical: {style: BorderStyle.SINGLE, size: 3, color: 'D9E0E7'} };

const p = (text, opts={}) => new Paragraph({
  alignment: opts.align || AlignmentType.LEFT,
  spacing: { after: opts.after === undefined ? 110 : opts.after, line: opts.line || 276 },
  children: [new TextRun({ text, bold: !!opts.bold, italics: !!opts.italics, color: opts.color, size: opts.size || 20 })]
});

const h = (text, level=HeadingLevel.HEADING_1) => new Paragraph({
  heading: level,
  spacing: { before: level === HeadingLevel.HEADING_1 ? 220 : 150, after: 90 },
  children: [new TextRun(text)]
});

function cell(text, width, header=false, align=AlignmentType.LEFT) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    verticalAlign: VerticalAlign.CENTER,
    shading: header ? { fill: navy, type: ShadingType.CLEAR } : undefined,
    margins: { top: 70, bottom: 70, left: 80, right: 80 },
    children: [new Paragraph({ alignment: align, spacing: { after: 0 }, children: [new TextRun({ text: String(text), bold: header, color: header ? 'FFFFFF' : '222222', size: 18 })] })]
  });
}

function infoTable(rows) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2450, 6910], borders,
    rows: rows.map(([a,b], i) => new TableRow({ children: [
      new TableCell({ width: {size:2450,type:WidthType.DXA}, shading:{fill:i%2?'EDF3F8':'DDEAF5',type:ShadingType.CLEAR}, margins:{top:70,bottom:70,left:80,right:80}, children:[new Paragraph({spacing:{after:0},children:[new TextRun({text:a,bold:true,color:navy,size:18})]})]}),
      new TableCell({ width: {size:6910,type:WidthType.DXA}, shading:{fill:i%2?'FFFFFF':'F8FAFC',type:ShadingType.CLEAR}, margins:{top:70,bottom:70,left:80,right:80}, children:[new Paragraph({spacing:{after:0},children:[new TextRun({text:b,size:18})]})]})
    ]}))
  });
}

function resultsTable(rows) {
  const widths = [1700, 1000, 1500, 1500, 3660];
  return new Table({
    width: { size: 9360, type: WidthType.DXA }, columnWidths: widths, borders,
    rows: [new TableRow({ tableHeader: true, children: [
      cell('Group', widths[0], true), cell('Atoms', widths[1], true, AlignmentType.CENTER),
      cell('Mean shift (eV)', widths[2], true, AlignmentType.CENTER), cell('Std. dev. (eV)', widths[3], true, AlignmentType.CENTER),
      cell('Atom indices', widths[4], true)
    ]}), ...rows.map((r,i) => new TableRow({ children: [
      cell(r.group.replaceAll('_',' '), widths[0]),
      cell(r.multiplicity, widths[1], false, AlignmentType.CENTER),
      cell(Number(r.mean_cls_eV).toFixed(3), widths[2], false, AlignmentType.CENTER),
      cell(Number(r.std_cls_eV).toFixed(3), widths[3], false, AlignmentType.CENTER),
      cell(r.atom_indices, widths[4])
    ]}))]
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: 'Arial', size: 20, color: '222222' }, paragraph: { spacing: { after: 110, line: 276 } } } },
    paragraphStyles: [
      { id:'Title', name:'Title', basedOn:'Normal', next:'Normal', run:{font:'Arial',size:42,bold:true,color:navy}, paragraph:{alignment:AlignmentType.CENTER,spacing:{before:0,after:140}} },
      { id:'Subtitle', name:'Subtitle', basedOn:'Normal', next:'Normal', run:{font:'Arial',size:22,color:gray}, paragraph:{alignment:AlignmentType.CENTER,spacing:{after:180}} },
      { id:'Heading1', name:'Heading 1', basedOn:'Normal', next:'Normal', quickFormat:true, run:{font:'Arial',size:28,bold:true,color:navy}, paragraph:{keepNext:true,spacing:{before:220,after:90},outlineLevel:0} },
      { id:'Heading2', name:'Heading 2', basedOn:'Normal', next:'Normal', quickFormat:true, run:{font:'Arial',size:23,bold:true,color:blue}, paragraph:{keepNext:true,spacing:{before:150,after:70},outlineLevel:1} }
    ]
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 900, right: 900, bottom: 850, left: 900, header: 400, footer: 400 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, spacing:{after:0}, children:[new TextRun({text:'QUANTUM ESPRESSO · CORE-LEVEL SHIFTS',color:'7A8793',size:15})] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, spacing:{after:0}, children:[new TextRun({text:'Planar Zn-porphyrin report  |  ',color:'7A8793',size:15}), new TextRun({children:[PageNumber.CURRENT],color:'7A8793',size:15})] })] }) },
    children: [
      new Paragraph({ style:'Title', children:[new TextRun('Planar Zn-Porphyrin')]}),
      new Paragraph({ style:'Title', children:[new TextRun('Initial-State Core-Level Shifts')]}),
      new Paragraph({ style:'Subtitle', children:[new TextRun('Completed Planar calculation and structural comparison with PLDC')]}),
      new Paragraph({ alignment:AlignmentType.CENTER, spacing:{after:160}, children:[new TextRun({text:'1 August 2026',size:19,color:gray})] }),
      new Paragraph({ alignment:AlignmentType.CENTER, spacing:{after:180}, children:[new ImageRun({data:fs.readFileSync(comparison),transformation:{width:610,height:337},type:'png',altText:{title:'Planar and PLDC structure comparison',description:'Side-by-side molecular structures with the two COO groups added in PLDC highlighted.',name:'Structure comparison'}})] }),
      h('Executive summary'),
      p('The Planar calculation is complete. Initial-state C 1s and N 1s shifts were evaluated for the requested carbon sites and all four nitrogen atoms. The twelve Cw atoms were deliberately excluded from the core-excited set.'),
      p('The PLDC file is included and plotted structurally for comparison. A numerical PLDC core-level-shift spectrum is not reported because the supplied isolated-molecule geometry does not uniquely specify its charge/protonation state; this choice materially changes the electronic calculation.'),
      h('Completed calculation at a glance'),
      infoTable([
        ['Structure','Planar ZnC44H28N4 (77 atoms)'],
        ['Selected sites','32 carbon atoms and all 4 nitrogen atoms'],
        ['Excluded sites','12 Cw carbon atoms: 7–12 and 36–41'],
        ['SCF convergence','35 electronic iterations; total energy −739.91432023 Ry'],
        ['Runtime','SCF: 15 min 57 s; initial_state.x analysis: 13 s'],
        ['References','Carbon shifts relative to mean(Cb); nitrogen shifts relative to mean(all N)']
      ]),

      new Paragraph({children:[new PageBreak()]}),
      h('Method and calculation settings'),
      p('The calculation follows the Quantum ESPRESSO initial-state core-level-shift workflow. Normal and core-excited pseudopotential species are present in a single self-consistent calculation. Each requested atom is mapped to its corresponding normal/core-excited pair by initial_state.x; Cw atoms remain mapped to a duplicate normal-carbon species and therefore are not excited.'),
      infoTable([
        ['Quantum ESPRESSO','Version 7.5; pw.x followed by initial_state.x'],
        ['Exchange–correlation','PBE'],
        ['Boundary conditions','25 Å cubic cell; isolated-molecule Martyna–Tuckerman correction'],
        ['Brillouin-zone sampling','Γ point'],
        ['Plane-wave cutoffs','30 Ry wave functions; 180 Ry charge density'],
        ['Occupations','Marzari–Vanderbilt smearing, 0.02 Ry'],
        ['Electronic convergence','conv_thr = 1×10⁻⁶; local-TF mixing, β = 0.20'],
        ['Parallel execution','4 MPI processes']
      ]),
      h('Atom groups', HeadingLevel.HEADING_2),
      p('The following assignments reproduce the requested indexing. Cw is intentionally absent from the calculated shift table.'),
      resultsTable(carbonGroups),
      h('Nitrogen groups', HeadingLevel.HEADING_2),
      resultsTable(nitrogenGroups),
      p('All values are relative shifts, not absolute experimental binding energies. A positive value denotes a higher binding energy relative to the stated reference.', {italics:true,color:gray,size:18}),

      new Paragraph({children:[new PageBreak()]}),
      h('Planar C 1s spectral envelopes'),
      new Paragraph({ alignment:AlignmentType.CENTER, spacing:{after:120}, children:[new ImageRun({data:fs.readFileSync(spectrum),transformation:{width:640,height:427},type:'png',altText:{title:'Planar carbon core-level shift envelopes',description:'Blue and red Gaussian-broadened carbon core-level shift envelopes for the selected atom groups.',name:'Planar spectra'}})] }),
      p('Blue envelope: CL,alpha + C alpha + CM. Red envelope: CL,beta + C beta + Cb. Each calculated atom contributes a unit-area Gaussian with FWHM = 0.35 eV, so the curves are a visualization of the discrete shifts rather than additional Quantum ESPRESSO data. Cw does not contribute.'),
      p('The common normalization preserves the relative atom-count weighting across the two envelopes. The underlying per-atom values remain available in the CSV file for alternative broadening or referencing.'),
      new Paragraph({children:[new PageBreak()]}),
      h('Planar versus PLDC structure'),
      new Paragraph({ alignment:AlignmentType.CENTER, spacing:{after:90}, children:[new ImageRun({data:fs.readFileSync(comparison),transformation:{width:640,height:353},type:'png',altText:{title:'Planar versus PLDC',description:'Molecular structure comparison highlighting the two added COO groups of PLDC.',name:'Planar PLDC comparison'}})] }),
      p('Planar: ZnC44H28N4. PLDC file: ZnC46H26N4O4. Relative to Planar, the PLDC coordinates contain two added COO groups and two fewer hydrogen atoms.'),

      new Paragraph({children:[new PageBreak()]}),
      h('PLDC calculation status and required decision'),
      p('The supplied PLDC XYZ file contains COO fragments without acidic hydrogen atoms. For an isolated calculation, the geometry can therefore represent a dianion (total charge −2), or it may require a different neutral/open-shell treatment; alternatively, two hydrogen atoms may need to be added to model two COOH groups. These choices are not interchangeable and cannot be inferred safely from XYZ coordinates alone.'),
      p('Prepared PLDC input templates are included in the comparison folder, but no incomplete or unconverged PLDC result is presented as a core-level-shift spectrum. Once the intended chemical state is confirmed, the same selected-site workflow and the same spectral broadening can be applied for a defensible numerical comparison.'),
      h('Convergence and interpretation notes'),
      p('The 25 Å cell and 30/180 Ry cutoffs are working settings for this completed run. Before publication-quality absolute comparisons, verify convergence with respect to cell size, plane-wave cutoffs, pseudopotential family, smearing, and molecular charge/spin. Experimental XPS comparison may also require a uniform energy alignment and consideration of final-state screening.'),
      h('Organized file package'),
      infoTable([
        ['structure/','Planar XYZ file and molecular figures'],
        ['inputs/','Completed Planar SCF and initial_state.x inputs'],
        ['outputs/','Converged Planar SCF and initial_state.x outputs'],
        ['results/','Per-atom CSV, group summary CSV, and spectrum PNG/PDF'],
        ['comparison/','PLDC XYZ, structural comparison PNG/PDF, and prepared PLDC templates'],
        ['scripts/','Reproducible preparation, analysis, and plotting scripts'],
        ['pseudopotentials/','Pseudopotentials used by the Planar workflow'],
        ['archive_full_C_N/','Earlier all-C/all-N calculation retained for traceability']
      ]),
      h('Reproducibility statement'),
      p('The CSV tables are the numerical source of truth for the reported shifts. The figures can be regenerated from the included scripts without changing the Quantum ESPRESSO output files.')
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(out, buffer);
  console.log(out);
});
