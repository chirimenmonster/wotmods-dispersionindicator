package 
{
	import Math;
	import flash.display.Sprite;
	import LabelContainer;
	
	/**
	 * ...
	 * @author Chirimen
	 */
	public class PanelContainer extends Sprite 
	{
		public var fieldWidth:int = 0;
		public var fieldHeight:int = 0;

		private var paddingTop:int = 2;
		private var paddingBottom:int = 2;
		private var paddingLeft:int = 4;
		private var paddingRight:int = 4;
		
		public function PanelContainer(config:Array):void
		{
			super();
			
			var i:int;
			var y:int = 0;
			var anchorX:int = 0;
			var line:LabelContainer;
			
			var labels:Array = [ "label0", "long label1", "short2" ];
			var unit:Array = [ "rad/100", "s", "km/h" ];

			y = paddingTop;
			for each (var c:Object in config) {
				line = new LabelContainer();
				addChild(line);
				line.init(c.label, c.unit);
				line.x = 0;
				line.y = y;
				if (anchorX < line.anchorX) {
					anchorX = line.anchorX;
				}
				fieldHeight = y + line.height;
				y += 16;
			}
			fieldHeight += paddingBottom;
			for (i = 0; i < numChildren; i++) {
				line = getChildAt(i) as LabelContainer;
				line.x = anchorX - line.anchorX + paddingLeft;
				fieldWidth = Math.max(fieldWidth, line.x + line.width + paddingRight)
			}
			graphics.beginFill(0x000000);
			graphics.drawRect(0, 0, fieldWidth, fieldHeight);
		}
	}
	
}