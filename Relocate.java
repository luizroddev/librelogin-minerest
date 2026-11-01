import java.io.File;
import java.util.LinkedHashMap;
import java.util.Map;
import me.lucko.jarrelocator.JarRelocator;

/** Build-only reproduction of the public upstream package relocation rules. */
public final class Relocate {
    public static void main(String[] args) throws Exception {
        Map<String, String> rules = new LinkedHashMap<>();
        for (int index = 2; index < args.length; index += 2) {
            rules.put(args[index], args[index + 1]);
        }
        new JarRelocator(new File(args[0]), new File(args[1]), rules).run();
    }
}
