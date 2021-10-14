  <script>
    // const hubUrl = "http://localhost:8000/";
    const hubUrl = "https://girder.hub.yt/";
    function getValues() {
        var Tmin = parseInt( $('#Tmin').val(), 10 );
        if (isNaN(Tmin)) Tmin = 0;
        var Tmax = parseInt( $('#Tmax').val(), 10 );
        if (isNaN(Tmax)) Tmax = 10000;
        var Pmin = parseInt( $('#Pmin').val(), 10 );
        if (isNaN(Pmin)) Pmin = 0;
        var Pmax = parseInt( $('#Pmax').val(), 10 );
        if (isNaN(Pmax)) Pmax = 10000;
        return {
            Tmin: Tmin,
            Tmax: Tmax,
            Pmin: Pmin,
            Pmax: Pmax
        }
    };
    $(document).ready(function() {
        var table = $('#example').DataTable( {
            "processing": true,
            "serverSide": true,
            "search": {
                return: true
            },
            "ajax": {
                "url": hubUrl + "api/v1/qmc/table",
                "data": function(d) {
                    d.sort = d.columns[d.order[0].column].data;
                    d.limit = d.length;
                    d.offset = d.start;
                    d.sortdir = d.order[0].dir === "asc" ? 1 : -1;
                    var values = getValues();
                    d.Tmin = values.Tmin
                    d.Tmax = values.Tmax
                    d.Pmin = values.Pmin
                    d.Pmax = values.Pmax
                }
            },
            "columns": [
                {
                    "data": "name",
                    "render": function(data, type, row, meta) {
                        if (type === 'display') {
                            var itemId = row.DT_RowData.itemId;
                            var entry = '<a href="' + hubUrl + '#item/' + itemId + '">' + data + '</a>';
                            entry += '<a href="' + hubUrl + 'api/v1/item/' + itemId + '/download">';
                            entry += '<i class="fa fa-download"></i>';
                            return entry;
                        }
                        return data;
                    }
                },
                {"data": "T"},
                {"data": "P"},
                {"data": "dft"},
                {"data": "ens"}
            ]   
        });
        $('#Tmin, #Tmax, #Pmin, #Pmax').change( function() {
            table.draw();
        });
    } );

    $('#downloadButton').on('click', function(event) {
        $.ajax({
          type: "GET",
          url: hubUrl + "api/v1/qmc/download",
          data: getValues(),
          xhrFields: {
            responseType: 'blob' // to avoid binary data being mangled on charset conversion
          },
          success: function(blob, status, xhr) {
              // check for a filename
              var filename = "";
              var disposition = xhr.getResponseHeader('Content-Disposition');
              if (disposition && disposition.indexOf('attachment') !== -1) {
                  var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                  var matches = filenameRegex.exec(disposition);
                  if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
              }

              if (typeof window.navigator.msSaveBlob !== 'undefined') {
                  // IE workaround for "HTML7007: One or more blob URLs were revoked by closing the blob for which they were created. 
                  // These URLs will no longer resolve as the data backing the URL has been freed."
                  window.navigator.msSaveBlob(blob, filename);
              } else {
                  var URL = window.URL || window.webkitURL;
                  var downloadUrl = URL.createObjectURL(blob);

                  if (filename) {
                      // use HTML5 a[download] attribute to specify filename
                      var a = document.createElement("a");
                      // safari doesn't support this yet
                      if (typeof a.download === 'undefined') {
                          window.location.href = downloadUrl;
                      } else {
                          a.href = downloadUrl;
                          a.download = filename;
                          document.body.appendChild(a);
                          a.click();
                      }
                  } else {
                      window.location.href = downloadUrl;
                  }

                  setTimeout(function () { URL.revokeObjectURL(downloadUrl); }, 100); // cleanup
              }
          }
      });
    });
  </script>
