    socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    socket.on('connect', function() {
        socket.emit('init', {'namespace': namespace});
    }); 

    socket.on('init_response', function(msg) {
      render =  function ( data, meta, row ) {return data.label;};
      thumb_render = function ( data, meta, row ) {return '<img class="thumbs" src="'+data+'"/>';};
      data = JSON.parse(msg["data"]);
      fields = JSON.parse(msg["fields"]);
      columns = JSON.parse(msg["columns"]);
      columnDefs = JSON.parse(msg["columnDefs"]);

      for(i=0;i<columns.length;i++){
        if(columns[i]['render'] == 'render'){
          columns[i]['render'] = render;
        };
        if(columns[i]['render'] == 'thumb_render'){
          columns[i]['render'] = thumb_render;
        };
      };
      //columns = [{'data': 'select-checkbox'}, {'data': 'id'}, {'data': 'name'}, {'data': 'category', 'render': render}, {'data': 'timestamp'}, {'data': 'assigned'}, {'data': 'url'}, {'data': 'tags'}, {'data': 'description'}, {'data': 'thumbnail', 'render': thumb_render}]
      


      editor = new $.fn.dataTable.Editor( {
          data: data,
          ajax: function ( method, url, d, successCallback, errorCallback ) {
            var output = { data: [] };
            for(var k in d.data); //get the id

            if ( d.action === 'create' ) {
              socket.emit('create', {'namespace': namespace, 'data': d.data[k], 'multiple': 'false'});
            }
            else if ( d.action === 'edit' ) {
              socket.emit('update', {'namespace': namespace, 'id': k, 'data':d.data[k]});
            }
            else if ( d.action === 'remove' ) {
              var k = [];
              $.each( d.data, function (id) {
                k.push(id);
              } );
              socket.emit('remove', {'namespace': namespace, 'ids': k});
            }
            successCallback(output);
          },
          table: '#' + namespace,
          idSrc:  'id',
          fields: fields
      } );   

      $('#' + namespace).on( 'click', 'tbody td:not(:first-child)', function (e) {
        var category = $(this).text();
        editor.inline( this, {
          drawType: 'page',
          onBlur: 'submit',
          onReturn: 'submit',
          submit: 'changed'
        } );

        $("div.DTE_Field_InputControl select option:contains('" + category + "')").attr("selected", "selected");
        $("div.DTE_Field_InputControl select option:contains('" + category + "')").prop("selected", "selected");
      } );  

      table = $('#' + namespace).DataTable( {
          "dom": 't<"bottom"irp><"clear">',
          "pageLength": 100,
          "data": data,
          "rowId": 'id',
          "columns": columns,        
          "columnDefs": columnDefs,      
          "order": [[ 1, "desc" ]],        
          "select": {
              "style": 'os',
              "selector": 'td:first-child'
          },
          buttons: [
            { extend: 'create', editor: editor },
            { extend: 'edit',   editor: editor },
            { extend: 'remove', editor: editor }
          ]  
      });    
    });    

    socket.on('add_response', function(msg) {
      data = JSON.parse(msg["data"]);
      category = data['category']['label'];
      file_id = data['id'];
      myDropzone.options.url = "upload?category=" + category + "&file_id=" + file_id;
      console.log(myDropzone.options.url);
      myDropzone.options.autoProcessQueue = true;
      myDropzone.processQueue();      
      table.row.add(data).draw();
    })

    socket.on('update_response', function(msg) {
      d = JSON.parse(msg.data);
      table.row.add(d).draw();
    })

    socket.on('delete_response', function(msg) {
      data = JSON.parse(msg['ids']);
      for(i=0;i<data.length;i++){
        id = data[i];
        table.row('#' + parseInt(id)).remove().draw();
      }
    })

    $('.table-len').on("click", function(event){
      var length = $(this).attr('value')
      table.page.len(length).draw();
    });

    $('.table-search').on( 'keyup', function () {
      table.search( this.value ).draw();
    } );   

