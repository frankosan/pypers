var SmartCanvas = {}

SmartCanvas.setup = function(canvas, isInitialized, context) {
    //don't redraw if we did once already
    if (isInitialized) return;

    var blueColors = [
        'rgba(7, 160, 218, .1)',
        'rgba(7, 160, 218, .2)',
        'rgba(7, 160, 218, .3)',
        'rgba(7, 160, 218, .4)'
    ];

    var redColors = [
        'rgba(213, 50, 60, .2)',
        'rgba(213, 50, 60, .4)',
        'rgba(213, 50, 60, .6)',
        'rgba(213, 50, 60, .8)'
    ];

    var shade = canvas.getAttribute('data-color-shade');

    var particlesNum = 100,
        particles = [],
        colors = eval(shade + 'Colors'),
        ctx = canvas.getContext('2d'),
        w = window.innerWidth,
        h = window.innerHeight;

    canvas.width  = w;
    canvas.height = h;
    canvas.className = 'container--canvas';

    var togoto = null;
    function Factory() {
        var _randomVelocity = function() {
            return (Math.round( Math.random() * 2) - 0.5) / 10;
        };
        this.x    = Math.round( Math.random() * w);
        this.y    = Math.round( Math.random() * h);
        this.rad  = ~~( Math.random() * 4) + 1;
        this.rgba = colors[ Math.round( Math.random() * 4) ];
        this.vx   = _randomVelocity();
        this.vy   = _randomVelocity();

        this.move = function(fps) {
            if(togoto) {
                var dx = togoto.x - this.x;
                var dy = togoto.y - this.y;
                this.vx = dx/fps * particlesNum/100;
                this.vy = dy/fps * particlesNum/100;
            }
            else {
                if(this.x > w) {
                    this.x = w;
                    this.vx = Math.abs(_randomVelocity()) * -1;
                }
                if(this.x < 0) {
                    this.x = 0;
                    this.vx = Math.abs(_randomVelocity());
                }
                if(this.y > h) {
                    this.y = h;
                    this.vy = Math.abs(_randomVelocity()) * -1;
                }
                if(this.y < 0) {
                    this.y = 0;
                    this.vy = Math.abs(_randomVelocity());
                }
            }

            this.x += this.vx;
            this.y += this.vy;
        };

        this.changeDirection = function() {
            this.vx   = Math.round( Math.random() * 2) - 0.5;
            this.vy   = Math.round( Math.random() * 2) - 0.5;
        };

        this.tilt = ~~(Math.random() * 180);
    }

    function HexaShape(x, y, rad, tilt) {

        var pts = [30, 90, 150, 210, 270, 330],
            i = 0;

        // jshint validthis:true
        for(i = 0; i < pts.length; i++) {
            this['pt'+(i+1)] = {
                x: Math.cos((pts[i] + tilt)*Math.PI/180) * rad + x,
                y: Math.sin((pts[i] + tilt)*Math.PI/180) * rad + y
            };
        }
    }

    function findDistance(p1,p2){
        return Math.sqrt( Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2) );
    }

    function draw(deltaT) {
        ctx.clearRect(0, 0, w, h);
        ctx.font = '9px Arial';
        ctx.globalCompositeOperation = 'destination-over';

        for(var i = 0;i < particlesNum; i++){
            var particle = particles[i];
            var factor = 1;

            ctx.strokeStyle = particle.rgba;
            ctx.fillStyle   = particle.rgba;

            for(var j = 0; j<particlesNum; j++){

                var neighbor = particles[j];
                ctx.lineWidth = 1;
                ctx.lineCap = 'round';

                if(findDistance(particle, neighbor) < 80){
                    ctx.strokeStyle = particle.rgba;
                    ctx.beginPath();
                    ctx.moveTo(particle.x, particle.y);
                    ctx.lineTo(neighbor.x, neighbor.y);

                    ctx.stroke();
                    if(particle.rgba === neighbor.rgba) {
                        factor += 3;
                    }
                }
            }


            var hexagon = new HexaShape(
                particle.x,
                particle.y,
                particle.rad*factor,
                particle.tilt
            );
            ctx.beginPath();
            ctx.moveTo(hexagon.pt1.x, hexagon.pt1.y);
            ctx.lineTo(hexagon.pt2.x, hexagon.pt2.y);
            ctx.lineTo(hexagon.pt3.x, hexagon.pt3.y);
            ctx.lineTo(hexagon.pt4.x, hexagon.pt4.y);
            ctx.lineTo(hexagon.pt5.x, hexagon.pt5.y);
            ctx.lineTo(hexagon.pt6.x, hexagon.pt6.y);
            ctx.fill();
            ctx.closePath();


            particle.move(deltaT);

        }
    }

    function resizeCanvas() {
        w = canvas.width  = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }

    window.requestAnimFrame = (function(){
        return  window.requestAnimationFrame ||
        window.webkitRequestAnimationFrame ||
        window.mozRequestAnimationFrame    ||
        function( callback ){
            window.setTimeout(callback, 1000 / 60);
        };
    })();

    var resizing = null;
    window.onresize = function() {
        if(resizing) {
            window.clearTimeout(resizing);
            resizing = null;
        }
        resizing = window.setTimeout(resizeCanvas, 300);
    };

    (function init(){
        for(var i = 0; i < particlesNum; i++){
        particles.push(new Factory());
        }
    })();

    (function animLoop() {
        var lastFrame = +(new Date());

        function loop(now) {
            window.requestAnimFrame(loop);
            draw(now - lastFrame);
            lastFrame = now;
        }

        loop(lastFrame);
    })();
}

exports.setup = SmartCanvas.setup;
