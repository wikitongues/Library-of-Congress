#!/usr/bin/env node

'use strict';
var Airtable = require('airtable');
var fs = require('fs');
var destination = process.argv[3]

var single = process.argv[2];

var fields = [
  'Identifier',
  'Title',
  'Creator',
  'Description',
  'Subject: Top level genealogy per language',
  'Subject: Language Continent of Origin',
  'Subject: Language Nation of Origin',
  'Subject: Speaker Genders',
  'Contributor: Speakers',
  'Contributor: Caption Authors',
  'Contributor: Videographer',
  'Contributor: Description',
  'Date Created',
  'Type',
  'Format',
  'Language names',
  'Languages: Speaker preferred names',
  'Languages: ISO Code (639-3)',
  'Languages: Glottocode',
  'Languages: Dialect Glottocode',
  'Languages: Macrolanguage ISO Code',
  'Caption Languages',
  'Caption Languages: ISO Code (639-6)',
  'Caption Languages: Glottocode',
  'Caption File Identifier',
  'Caption File Links',
  'Coverage: Video Nation',
  'Coverage: Video Territory',
  'Coverage: Distribution',
  'Rights',
  'Publisher',
  'Date Received',
  'Encoded Data',
  'Tagged Data',
  'Duration',
  'Format T',
  'Format Profile',
  'Codec ID',
  'File size',
  'Format Info',
  'Format Settings',
  'Format Settings CABAC',
  'Format Settings ReFrames',
  'Codec ID/Info',
  'Bit rate',
  'Width',
  'Height',
  'Display Aspect Ratio',
  'Frame Rate',
  'Standard',
  'Color Space',
  'Chroma Subsampling',
  'Bit Depth',
  'Scan Type',
  'Bits (Pixel*Frame)',
  'Stream size',
  'Color range',
  'Color primaries',
  'Transfer characteristics',
  'Matrix coefficients',
  'Codec configuration box',
  'Format audio',
  'Format/Info Audio',
  'Bit Rate Audio',
  'Bit rate mode audio',
  'Codec ID Audio',
  'Channel(s)',
  'Channel layout',
  'Compression mode',
  'Sampling rate',
  'Stream size audio',
  'Subjects Reference ID: Ethnologue'
];

try {
  var base = new Airtable({apiKey: process.env.APIKEY}).base(process.env.BASE);

  base('Oral Histories').select({
      view: "Archival View (Comprehensive)",
      cellFormat: "string",
      timeZone: "America/New_York",
      userLocale: "en-ca",
      filterByFormula: "Identifier='"+single+"'",
      fields
  }).eachPage(function page(records, fetchNextPage) {
    if (!Array.isArray(records) || !!records.length) {
      records.forEach(function(record) {
          const content = [
            `Metadata for ${record.get('Identifier')}`,

            ...fields.map(field => `${field}: ${record.get(field)}`)
          ].join('\n');

          fs.writeFileSync(`${destination}/loctemp__${single}/${record.get('Identifier')}__metadata.txt`, content);
      });
      fetchNextPage();
    } else {
      console.log(`\x1b[31mWarning! ID '${single}' not found on airtable.`);
      return process.exit(1);
    }
  }, function done(err) {
      if (err) { 
        console.error(err); 
        return process.exit(1);
      }
  });
} catch (e) {
  console.error(e);
  return process.exit(1);
}