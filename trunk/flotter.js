function kbytesFormatter(val, axis) {
   function fmt(n, sf) {
      return Math.round(n*Math.pow(10,sf))/Math.pow(10,sf);
   }
   return fmt(val/1024,2) + 'Kb';
}
function uriFormatter(uri, maxlength) {
   if(maxlength == null) maxlength=200;
   if (uri.length > maxlength) {
      return uri.substr(0, 3*parseInt(maxlength/4))+' ... '+uri.substr(3*parseInt(maxlength/4), uri.length);
   }
   return uri;
}

var options = {
        points: { show: true },
        lines: { show: true, lineWidth: 3, fill: true },
        xaxis: { mode: "time" },
        yaxis: { tickFormatter: kbytesFormatter, tickDecimals: 2, labelWidth: 56 },
        selection: { mode: "x" },
        grid: { clickable: false, mouseCatchingArea: 6, triggerOnMouseOver: true }
    };
    
$(function () {
    
   max_value += parseInt(0.01 * max_value);
    
   plot = $.plot($("#placeholder"), [d], options);
   
   /* Commented out until this is solved
    * http://groups.google.com/group/flot-graphs/browse_thread/thread/10a7eee60fd25d32
   overview = $.plot($("#overview"), [d], {
      lines: { show: true, lineWidth: 1, fill: true },
      shadowSize: 0,
        xaxis: { ticks: [], mode: "time" },
      yaxis: { ticks: [], min: min_value, max: max_value },
      selection: { mode: "x" }
   });
    */
    

    // now connect the two
    var internalSelection = false;
    
    $("#placeholder").bind("selected", function (event, area) {
       //console.log("event on #placeholder");
        printURLs(area.x1, area.x2);
        /*
        plot = $.plot($("#placeholder"), [d],
                      $.extend(true, {}, options, {
                          xaxis: { min: area.x1, max: area.x2 }
                      }));
        
        if (internalSelection)
            return; // prevent eternal loop
        internalSelection = true;
        overview.setSelection(area);
        internalSelection = false;
        */
    });
    
   
    $("#overview").bind("selected", function (event, area) {
       //console.log("event on #overview");
       // do the zooming
       if (internalSelection)
         return;
       internalSelection = true;
       plot.setSelection(area);
       internalSelection = false;
    });
    
    
});


function __get_flux(value, prev) {
   if (prev != null) {
      if (value > prev) {
         return '+' + (value-prev);
      } else if (value < prev) {
         return ''+ (value-prev);
      }
   }
   return '';
}

function printURLs(x1, x2) {
   $('tbody', $('#urls')).remove();
   $('thead', $('#urls')).remove();
   
   $('#urls').append(
           $('<thead></thead>').append(
                   $('<tr></tr>').append(
                         $('<th></th>').text('Memory size')
                                 ).append(
                         $('<th></th>').text('Change')
                                 ).append(
                         $('<th></th>').text('URI')
                                 )
                     ) 
            );
   
   
   var keep = new Array();
   var prev = null;
   var line;
   $.each(d, function() {
      if (this[0] >= x1 && this[0] < x2) {
         line = kbytesFormatter(this[1]);
         $('#urls').append(
                           $('<tbody></tbody>').append(
                                                       $('<tr></tr>').append(
                                                                             $('<td></td>').text(kbytesFormatter(this[1])).attr('align','right')
                                                                    ).append(
                                                                             $('<td></td>').text(__get_flux(this[1], prev)).attr('align','right')
                                                                    ).append(
                                                                             $('<td></td>').text(uriFormatter(this[2]))
                                                                    )

                           )
                           );
         
         if (prev != null) {
            if (this[1] > prev) {
               line += ' (+' + (this[1]-prev) + ')';
            } else if (this[1] < prev) {
               line += ' (' + (this[1]-prev) + ')';
            }
         }
         line += ' ' + this[2]
         keep.push(line);
         prev = this[1];
      }
   });
   return keep;
}


function resetPlotSelection() {
   location.href=location.href;
}

