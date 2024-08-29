from eggtools.utils.MarginCalculator import MarginCalculator

image_width = 256
image_height = 256

# a value between 1 and 100
percent = 1

percent_norm = float(percent / 100)
margin_u = percent_norm
margin_v = percent_norm

margins, image_usage = MarginCalculator.get_margined_by_ratio(
    image_width, image_height, margin_u, margin_v
)

used_width, used_height = image_usage
margin_x, margin_y = margins

print(f"Margin percent: {percent}%")
print(f"Initial image: {image_width}x{image_height}")
print(f"-=-=-=-=-=-=-")
print(f"Used space: {used_width}x{used_height}")
print(f"Margin space: {margin_x}x{margin_y}")
print(f"Texture loss: {100 - (used_width / image_width) * 100}%")
