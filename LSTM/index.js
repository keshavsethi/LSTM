let requestUrl = "https://raw.githubusercontent.com/keshavsethi/streamlit/master/csvjson.json";
url_post = "http://127.0.0.1:5000/predict_withone";


var t = $('#addrows').DataTable();
 
const cb1 = document.getElementById('accept1');
const cb2 = document.getElementById('accept2');
const cb3 = document.getElementById('accept3');
const cb4 = document.getElementById('accept4');
var slider1 = document.getElementById("myRange1");
var slider2 = document.getElementById("myRange2");
var slider3 = document.getElementById("myRange3");
var slider4 = document.getElementById("myRange4");

  $.getJSON(requestUrl
    ,function(data){
      console.log(data);
//data.filter(x.speed => !!x.speed);
        data.sort(function(a, b){
           return new Date(b.timestamp) - new Date(a.timestamp);
      });
        data_raw = [];
        course_raw  = [];
        rot_raw  = [];
	lat_raw =[];
        long_raw =[];
        heading_raw = [];
        let index = 0;
        for(let index1 in data){
          
          data_raw.push({ timestamp: data[index1].timestamp, speed: data[index1].speed });
          course_raw.push({ timestamp: data[index1].timestamp, course: data[index1].course });
          rot_raw.push({ timestamp: data[index1].timestamp, rot: data[index1].rot });
          lat_raw.push({ timestamp: data[index1].timestamp, lat: data[index1].latitude });
          long_raw.push({ timestamp: data[index1].timestamp, long: data[index1].longitude });
          heading_raw.push({ timestamp: data[index1].timestamp, heading: data[index1].heading });
          index++;
        }
         data_raw.reverse();
course_raw.reverse();
rot_raw.reverse();
lat_raw.reverse();
long_raw.reverse();
heading_raw.reverse();

          let timestamp = data_raw.map(function (val) { return val['timestamp']; });
console.log(timestamp);
          let speed = data_raw.map(function (val) { return val['speed']; });
         let course = course_raw.map(function (val) { return val['course']; });
         let rot = rot_raw.map(function (val) { return val['rot']; });
         let lat = lat_raw.map(function (val) { return val['lat']; });
         let long = long_raw.map(function (val) { return val['long']; });
         let heading = heading_raw.map(function (val) { return val['heading']; });





 var data1 = [{
    x: [timestamp[0]], 
    y: [speed[0]],
    mode: 'scatter',
    line: {color: 'red'}
  },{
    x: [timestamp[0]],
    y: [speed[0]],
    mode: 'scatter',
    line: {color: 'blue'}}
]

 var data2 = [{
    x: [timestamp[0]], 
    y: [course[0]],
    mode: 'scatter',
    line: {color: 'red'}
  }]


 var data3 = [{
    x: [timestamp[0]], 
    y: [rot[0]],
    mode: 'scatter',
    line: {color: 'red'}
  }]

 var data4 = [{
    x: [timestamp[0]], 
    y: [heading[0]],
    mode: 'scatter',
    line: {color: 'red'}
  }]

var layout1 = {
  xaxis: {
    type: 'date',
    title: 'Time(UTC)', 
	tickfont: {
      family: 'Old Standard TT, serif',
      size: 14,
      color: 'red'
    },
  },
  yaxis: {
    title: 'Speed'
  },
annotations:[]
};
var layout2 = {
  xaxis: {
    type: 'date',
    title: 'Time(UTC)', 
	tickfont: {
      family: 'Old Standard TT, serif',
      size: 14,
      color: 'red'
    },
  },
  yaxis: {
    title: 'Course'
  },
 
};
var layout3 = {
  xaxis: {
    type: 'date',
    title: 'Time(UTC)', 
	tickfont: {
      family: 'Old Standard TT, serif',
      size: 14,
      color: 'red'
    },
  },
  yaxis: {
    title: 'rot'
  },
 
};
var layout4 = {
  xaxis: {
    type: 'date',
    title: 'Time(UTC)', 
	tickfont: {
      family: 'Old Standard TT, serif',
      size: 14,
      color: 'red'
    },
  },
  yaxis: {
    title: 'heading'
  },
 
};
  Plotly.plot('graph1', data1, layout1);
  Plotly.plot('graph2', data2, layout2);  
  Plotly.plot('graph3', data3, layout3);  
  Plotly.plot('graph4', data4, layout4);    


  var cnt = 0;
  
  var interval = setInterval(function() {
    var position = {
    x:  [[lat[cnt+1]]],
    y: [[long[cnt+1]]]
    }
    var param = {
    a: [[speed[cnt+1]]],
    b: [[course[cnt+1]]], 
    c:  [[rot[cnt+1]]],
    d: [[heading[cnt+1]]]
    }

if(cb1.checked){
  (param.a[0])[0]= slider1.value;
}

if(cb2.checked){
(param.b[0])[0] = slider2.value;
}

if(cb3.checked){
(param.c[0])[0]= slider3.value;
}

if(cb4.checked){
(param.d[0])[0] = slider4.value;
}


let data1 = {values: [0,0,1,0,parseFloat((param.d[0])[0]), (position.x[0])[0], (position.y[0])[0],parseFloat((param.c[0])[0]), parseFloat((param.a[0])[0]),parseFloat((param.b[0])[0])]};


async function postData(url = '', data = {}) {
  const response = await fetch(url, {
    method: 'POST', 
    mode: 'cors',
    cache: 'no-cache', 
    credentials: 'same-origin', 
    headers: {
      'Content-Type': 'application/json'
    },
    referrerPolicy: 'no-referrer',
    body: JSON.stringify(data) 
  });
  return response.json();
}

postData(url_post, data1)
  .then(data => {
  var update1 = {
    x:  [[timestamp[cnt+1]], [timestamp[cnt+1]]],
    y: [[speed[cnt+1]], [data[8]]]
    }
console.log(data);
  var time1 = update1.x[0];
    var update2 = {
    x:  [[timestamp[cnt+1]]],
    y: [[course[cnt+1]]]
    }

  var time2 = update2.x[0];
    var update3 = {
    x:  [[timestamp[cnt+1]]],
    y: [[rot[cnt+1]]]
    }

  var time3 = update3.x[0];
    var update4 = {
    x:  [[timestamp[cnt+1]]],
    y: [[heading[cnt+1]]]
    }

if(cb1.checked){
 update1.y[0] =  [slider1.value];
}
else{
slider1.value = update1.y[0];
}
if(cb2.checked){
 update2.y[0] = [slider2.value];
}
else{
slider2.value =  update2.y[0];
}
if(cb3.checked){
 update3.y[0] = [slider3.value];
}
else {
slider3.value =  update3.y[0];
}
if(cb4.checked){
 update4.y[0]  = [slider4.value];
}
else {
slider4.value =  update4.y[0];
}
 var time4 = update4.x[0];

 var minuteView1 = {
       title: time1[0],
       xaxis: {
         range: [timestamp[cnt-1],timestamp[cnt+2]],
         autorange: true,
         showgrid: false,
         zeroline: false,
         showline: false,
         autotick: true,
         showticklabels: false
        },
annotations:[]
     };
if(data[2]-update1.y[0]>0.5){
var result = {
   // xref: 'timestamp',
    x: timestamp[cnt+2],
    y: update1.y[0],
      text: 'Annotation B',

    };
   console.log(layout1);
  minuteView1.annotations.push(result);
  t.row.add( [
            timestamp[cnt-1],
            update1.y[0],
            update2.y[0],
            update3.y[0],
            update4.y[0],
        ] ).draw( false );
}

var minuteView2 = {
       title: time2[0],
       xaxis: {
         range: [timestamp[cnt-1],timestamp[cnt+2]],
         autorange: true,
         showgrid: false,
         zeroline: false,
         showline: false,
         autotick: true,
         showticklabels: false
        }
     };
var minuteView3 = {
       title: time3[0],
       xaxis: {
         range: [timestamp[cnt-1],timestamp[cnt+2]],
         autorange: true,
         showgrid: false,
         zeroline: false,
         showline: false,
         autotick: true,
         showticklabels: false
        }
     };
var minuteView4 = {
       title: time4[0],
       xaxis: {
         range: [timestamp[cnt-1],timestamp[cnt+2]],
         autorange: true,
         showgrid: false,
         zeroline: false,
         showline: false,
         autotick: true,
         showticklabels: false
        }
     };

  Plotly.relayout('graph1', minuteView1);
  Plotly.extendTraces('graph1', update1, [0,1])
  Plotly.relayout('graph2', minuteView2);
  Plotly.extendTraces('graph2', update2, [0])
  Plotly.relayout('graph3', minuteView3);
  Plotly.extendTraces('graph3', update3, [0])
  Plotly.relayout('graph4', minuteView4);
  Plotly.extendTraces('graph4', update4, [0])
  });
  if(++cnt === 100000) clearInterval(interval);
  }, 5000);
  
    }
  );




////////////////////////////////////////////////////////




