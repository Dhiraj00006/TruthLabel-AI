export default function Upload() {
  return (
    <main>
      <h1>New scan</h1>
      <form>
        <label>Images (front/back/side)<input type="file" name="images" multiple /></label>
        <label>Declared net quantity<input type="number" name="net_quantity_declared" /></label>
        <label>Unit<input type="text" name="net_quantity_unit" /></label>
        <label>Package height (mm)<input type="number" name="package_height_mm" /></label>
        <label>Or listing URL / text<textarea name="listing_text" /></label>
        <button type="submit">Submit scan</button>
      </form>
    </main>
  );
}
