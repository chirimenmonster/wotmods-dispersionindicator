package com.chirimen.dispersionindicator
{
    import flash.display.Sprite;
    import flash.filters.DropShadowFilter;
    import Math;

    import com.chirimen.dispersionindicator.LineContainer;
	
    /**
     * ...
     * @author Chirimen
     */
    public class PanelContainer extends Sprite 
    {
        public var fieldWidth:int = 0;
        public var fieldHeight:int = 0;

        public function PanelContainer(config:Array, style:Object) : void
        {
            super();
			
            var i:int;
            var y:int = 0;
            var anchorX:int = 0;
            var line:LineContainer;
			
            y = style.paddingTop;
            for each (var c:Object in config) {
                line = new LineContainer();
                addChild(line);
                line.init(c.label, c.unit, c.valueWidth, style);
                line.name = c.name;
                line.x = 0;
                line.y = y;
                if (anchorX < line.anchorX) {
                    anchorX = line.anchorX;
                }
                fieldHeight = y + line.height;
                y += style.lineHeight;
            }
            fieldHeight += style.paddingBottom;
            for (i = 0; i < numChildren; i++) {
                line = getChildAt(i) as LineContainer;
                line.x = anchorX - line.anchorX + style.paddingLeft;
                fieldWidth = Math.max(fieldWidth, line.x + line.width + style.paddingRight);
            }
            setBackground(style);
            setFilter(style);
            alpha = style.alpha;
        }

        private function setBackground(style:Object) : void
        {
            if (style.hasOwnProperty("backgroundColor")) {
                var color:int = style.backgroundColor[0] << 16 + style.backgroundColor[1] << 8 + style.backgroundColor[2];
                var alpha:Number = style.backgroundColor[3] as Number;
                graphics.beginFill(color, alpha);
                graphics.drawRect(0, 0, fieldWidth, fieldHeight);
            }
        }

        private function setFilter(style:Object) : void
        {
            if (style.hasOwnProperty("filter")) {
                if (style.filter == "DROPSHADOW") {
                    var dropShadow:DropShadowFilter = new DropShadowFilter(0, 45, 0, 0.8, 8, 8, 3);
                    var filters:Array = [ dropShadow ];
                    for (var i:int = 0; i < numChildren; i++) {
                        var line:LineContainer = getChildAt(i) as LineContainer;
                        line.setFilters(filters);
                    }
                }
            }
        }

    }
	
}
